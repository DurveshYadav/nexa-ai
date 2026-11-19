
import pytest

from app.integrations.llm.schemas import LLMResponse, LLMToolCall
from app.services.v3.orchestrator import AgentOrchestrator
from app.tools.v3.context import ExecutionContext
from app.tools.v3.registration import build_tool_registry
from app.tools.v3.schemas.results import ToolError, ToolResult
from app.tools.v3.dependencies import ToolDependencies
from app.tools.v3.executor import ToolExecutor
from app.models.approval import AgentApproval
from app.services.conversation_service import conversation_service

class FakeProvider:
    def __init__(self, responses):
        self.responses = responses
        self.calls = []

    def generate(self, messages, tools=None):
        self.calls.append(messages.copy())

        response = self.responses.pop(0)

        if isinstance(response, Exception):
            raise response

        return response


class FakeExecutor:
    def __init__(self, results=None):
        self.results = results or []
        self.calls = []

    def execute(self, tool_name, arguments, context):
        self.calls.append(tool_name)

        if self.results:
            return self.results.pop(0)

        return ToolResult(success=True, data={"status": "shipped"})


def make_context():
    return ExecutionContext(
        user_id=1,
        customer_id=1,
        run_id="run-1",
        request_id="req-1",
        permissions=frozenset({"orders:read"}),
    )


def make_tool_call(name="get_order_status", call_id="call_1"):
    return LLMToolCall(
        id=call_id,
        name=name,
        arguments={"order_id": "ORD-10025"},
    )


def make_orchestrator(provider, executor=None, **kwargs):
    registry = build_tool_registry()

    return AgentOrchestrator(
        provider=provider,
        executor=executor or FakeExecutor(),
        registry=registry,
        tools=[],
        allowed_tools=frozenset({
            "get_order_status",
            "get_order_details",
        }),
        **kwargs,
    )


def test_orchestrator_returns_final_response():
    provider = FakeProvider([
        LLMResponse(content="Hello!", model="gpt-5-mini")
    ])

    orchestrator = make_orchestrator(provider)

    result = orchestrator.run("Hello", make_context(), "System prompt")

    assert result.status == "completed"
    assert result.content == "Hello!"
    assert result.iterations == 1
    assert len(provider.calls) == 1
    run_state = orchestrator.run_manager.get_run("run-1", 1)
    assert run_state.status == "completed"
    assert run_state.error_code is None


def test_orchestrator_executes_tool_and_returns_final_response():
    provider = FakeProvider([
        LLMResponse(
            content=None,
            model="gpt-5-mini",
            tool_calls=[make_tool_call()],
        ),
        LLMResponse(content="Your order is shipped.", model="gpt-5-mini"),
    ])

    executor = FakeExecutor()
    orchestrator = make_orchestrator(provider, executor)

    result = orchestrator.run("Check order", make_context(), "System prompt")

    assert result.status == "completed"
    assert result.content == "Your order is shipped."
    assert result.tool_calls_count == 1
    assert executor.calls == ["get_order_status"]
    history = orchestrator.run_manager.get_history("run-1", 1)

    assert len(history) == 1
    assert history[0].step_number == 1
    assert history[0].tool_call_id == "call_1"
    assert history[0].tool_name == "get_order_status"
    assert history[0].status == "completed"
    assert history[0].error_code is None
    assert history[0].duration_ms >= 0


def test_orchestrator_rejects_sensitive_tool_without_approval_context():
    provider = FakeProvider([
        LLMResponse(
            content=None,
            model="gpt-5-mini",
            tool_calls=[make_tool_call("cancel_order")],
        )
    ])

    executor = FakeExecutor()
    orchestrator = make_orchestrator(provider, executor)

    result = orchestrator.run(
        "Cancel order",
        make_context(),
        "System prompt",
    )

    assert result.status == "failed"
    assert result.error_code == "APPROVAL_CONTEXT_MISSING"
    assert result.approval_id is None
    assert executor.calls == []

    run_state = orchestrator.run_manager.get_run("run-1", 1)
    assert run_state.status == "failed"
    assert run_state.error_code == "APPROVAL_CONTEXT_MISSING"


def test_orchestrator_marks_run_failed_on_provider_error():
    provider = FakeProvider([
        RuntimeError("Provider unavailable")
    ])

    orchestrator = make_orchestrator(provider)

    result = orchestrator.run(
        "Hello",
        make_context(),
        "System prompt",
    )

    assert result.status == "failed"
    assert result.error_code == "LLM_PROVIDER_ERROR"

    run_state = orchestrator.run_manager.get_run("run-1", 1)
    assert run_state.status == "failed"
    assert run_state.error_code == "LLM_PROVIDER_ERROR"

def test_orchestrator_enforces_max_iterations():
    provider = FakeProvider([
        LLMResponse(
            content=None,
            model="gpt-5-mini",
            tool_calls=[make_tool_call()],
        )
    ])

    orchestrator = make_orchestrator(
        provider,
        max_iterations=1,
    )

    result = orchestrator.run("Check order", make_context(), "System prompt")

    assert result.status == "failed"
    assert result.error_code == "MAX_ITERATIONS_EXCEEDED"
    assert len(provider.calls) == 1


def test_orchestrator_enforces_max_tool_calls():
    provider = FakeProvider([
        LLMResponse(
            content=None,
            model="gpt-5-mini",
            tool_calls=[
                make_tool_call(call_id="call_1"),
                make_tool_call(call_id="call_2"),
            ],
        )
    ])

    executor = FakeExecutor()
    orchestrator = make_orchestrator(
        provider,
        executor,
        max_tool_calls=1,
    )

    result = orchestrator.run("Check order", make_context(), "System prompt")

    assert result.error_code == "MAX_TOOL_CALLS_EXCEEDED"
    assert result.tool_calls_count == 0
    assert executor.calls == []


def test_orchestrator_handles_provider_error():
    provider = FakeProvider([RuntimeError("Provider unavailable")])
    orchestrator = make_orchestrator(provider)

    result = orchestrator.run("Hello", make_context(), "System prompt")

    assert result.status == "failed"
    assert result.error_code == "LLM_PROVIDER_ERROR"


def test_orchestrator_stops_after_consecutive_tool_failures():
    failure = ToolResult(
        success=False,
        error=ToolError(
            code="EXECUTION_ERROR",
            message="Tool execution failed.",
        ),
    )

    provider = FakeProvider([
        LLMResponse(
            content=None,
            model="gpt-5-mini",
            tool_calls=[make_tool_call()],
        ),
        LLMResponse(
            content=None,
            model="gpt-5-mini",
            tool_calls=[make_tool_call(call_id="call_2")],
        ),
        LLMResponse(
            content=None,
            model="gpt-5-mini",
            tool_calls=[make_tool_call(call_id="call_3")],
        ),
    ])

    executor = FakeExecutor([failure, failure, failure])
    orchestrator = make_orchestrator(provider, executor)

    result = orchestrator.run("Check order", make_context(), "System prompt")

    assert result.status == "failed"
    assert result.error_code == "MAX_CONSECUTIVE_FAILURES"
    assert result.tool_calls_count == 3
    assert len(executor.calls) == 3


def test_orchestrator_handles_unknown_tool():
    provider = FakeProvider([
        LLMResponse(
            content=None,
            model="gpt-5-mini",
            tool_calls=[make_tool_call("unknown_tool")],
        ),
        LLMResponse(
            content="That tool is unavailable.",
            model="gpt-5-mini",
        ),
    ])

    registry = build_tool_registry()
    executor = ToolExecutor(
        registry=registry,
        dependencies=ToolDependencies(),
    )

    orchestrator = AgentOrchestrator(
        provider=provider,
        executor=executor,
        registry=registry,
        tools=[],
        allowed_tools=frozenset({"get_order_status"}),
    )

    result = orchestrator.run(
        "Check something",
        make_context(),
        "System prompt",
    )

    assert result.status == "completed"
    assert provider.calls[1][-1]["role"] == "tool"
    assert "UNKNOWN_TOOL" in provider.calls[1][-1]["content"]


def test_orchestrator_blocks_disallowed_tool():
    provider = FakeProvider([
        LLMResponse(
            content=None,
            model="gpt-5-mini",
            tool_calls=[make_tool_call("get_product_details")],
        ),
        LLMResponse(
            content="This tool is not available.",
            model="gpt-5-mini",
        ),
    ])

    executor = FakeExecutor()
    orchestrator = make_orchestrator(provider, executor)

    result = orchestrator.run(
        "Get product details",
        make_context(),
        "System prompt",
    )

    assert result.status == "completed"
    assert result.tool_calls_count == 1
    assert executor.calls == []
    assert "TOOL_NOT_ALLOWED" in provider.calls[1][-1]["content"]


def test_orchestrator_rejects_sensitive_tool_without_context_on_final_iteration():
    provider = FakeProvider([
        LLMResponse(
            content=None,
            model="gpt-5-mini",
            tool_calls=[make_tool_call("cancel_order")],
        )
    ])

    executor = FakeExecutor()
    orchestrator = make_orchestrator(
        provider,
        executor,
        max_iterations=1,
    )

    result = orchestrator.run(
        "Cancel order",
        make_context(),
        "System prompt",
    )

    assert result.status == "failed"
    assert result.error_code == "APPROVAL_CONTEXT_MISSING"
    assert executor.calls == []


def test_orchestrator_handles_unexpected_executor_exception():
    class RaisingExecutor:
        def execute(self, **kwargs):
            raise RuntimeError("Internal database details")

    provider = FakeProvider([
        LLMResponse(
            content=None,
            model="gpt-5-mini",
            tool_calls=[make_tool_call("get_order_status")],
        ),
        LLMResponse(
            content="I could not retrieve the order details.",
            model="gpt-5-mini",
        ),
    ])

    executor = RaisingExecutor()
    orchestrator = make_orchestrator(provider, executor)

    result = orchestrator.run(
        "Check my order status",
        make_context(),
        "System prompt",
    )

    assert result.status == "completed"
    assert len(provider.calls) == 2

    tool_message = provider.calls[1][-1]

    assert tool_message["role"] == "tool"
    assert "EXECUTION_ERROR" in tool_message["content"]
    assert "Internal database details" not in tool_message["content"]


def test_orchestrator_stops_after_repeated_executor_exceptions():
    class RaisingExecutor:
        def execute(self, **kwargs):
            raise RuntimeError("Internal database details")

    provider = FakeProvider([
        LLMResponse(
            content=None,
            model="gpt-5-mini",
            tool_calls=[make_tool_call("get_order_status", "call_1")],
        ),
        LLMResponse(
            content=None,
            model="gpt-5-mini",
            tool_calls=[make_tool_call("get_order_status", "call_2")],
        ),
        LLMResponse(
            content=None,
            model="gpt-5-mini",
            tool_calls=[make_tool_call("get_order_status", "call_3")],
        ),
    ])

    orchestrator = make_orchestrator(
        provider,
        RaisingExecutor(),
        max_consecutive_failures=3,
    )

    result = orchestrator.run(
        "Check my order status",
        make_context(),
        "System prompt",
    )

    assert result.status == "failed"
    assert result.error_code == "MAX_CONSECUTIVE_FAILURES"
    assert result.tool_calls_count == 3
    assert len(provider.calls) == 3

def test_orchestrator_records_multiple_tool_calls_in_order():
    provider = FakeProvider([
        LLMResponse(
            content=None,
            model="gpt-5-mini",
            tool_calls=[
                make_tool_call("get_order_status", "call_1"),
                make_tool_call("get_order_details", "call_2"),
            ],
        ),
        LLMResponse(
            content="Here are your order details.",
            model="gpt-5-mini",
        ),
    ])

    executor = FakeExecutor()
    orchestrator = make_orchestrator(provider, executor)

    result = orchestrator.run(
        "Check my order",
        make_context(),
        "System prompt",
    )

    history = orchestrator.run_manager.get_history("run-1", 1)

    assert result.status == "completed"
    assert result.tool_calls_count == 2
    assert executor.calls == [
        "get_order_status",
        "get_order_details",
    ]

    assert len(history) == 2
    assert [step.step_number for step in history] == [1, 2]
    assert [step.tool_call_id for step in history] == [
        "call_1",
        "call_2",
    ]
    assert all(step.status == "completed" for step in history)

def test_orchestrator_records_failed_tool_execution():
    provider = FakeProvider([
        LLMResponse(
            content=None,
            model="gpt-5-mini",
            tool_calls=[make_tool_call()],
        ),
        LLMResponse(
            content="I could not retrieve your order details.",
            model="gpt-5-mini",
        ),
    ])

    executor = FakeExecutor(results=[
        ToolResult(
            success=False,
            error=ToolError(
                code="ORDER_NOT_FOUND",
                message="Order was not found.",
            ),
        )
    ])

    orchestrator = make_orchestrator(provider, executor)

    result = orchestrator.run(
        "Check my order",
        make_context(),
        "System prompt",
    )

    history = orchestrator.run_manager.get_history("run-1", 1)

    assert result.status == "completed"
    assert len(history) == 1
    assert history[0].status == "failed"
    assert history[0].error_code == "ORDER_NOT_FOUND"
    assert history[0].tool_name == "get_order_status"

def test_orchestrator_stops_when_run_is_cancelled():
    provider = FakeProvider([
        LLMResponse(
            content=None,
            model="gpt-5-mini",
            tool_calls=[make_tool_call()],
        )
    ])

    executor = FakeExecutor()
    orchestrator = make_orchestrator(provider, executor)

    original_generate = provider.generate

    def generate_and_cancel(messages, tools=None):
        orchestrator.run_manager.cancel_run("run-1", 1)
        return original_generate(messages, tools)

    provider.generate = generate_and_cancel

    result = orchestrator.run(
        "Check my order",
        make_context(),
        "System prompt",
    )

    run_state = orchestrator.run_manager.get_run("run-1", 1)

    assert result.status == "failed"
    assert result.error_code == "RUN_CANCELLED"
    assert run_state.status == "cancelled"
    assert executor.calls == []

def test_orchestrator_creates_persistent_approval(
    db,
    test_user,
):
    user_id = test_user["id"]

    conversation = conversation_service.create_conversation(
        db=db,
        user_id=user_id,
        title="Cancel order test",
    )

    provider = FakeProvider([
        LLMResponse(
            content=None,
            model="gpt-5-mini",
            tool_calls=[make_tool_call("cancel_order")],
        )
    ])

    executor = FakeExecutor()
    orchestrator = make_orchestrator(provider, executor)

    context = ExecutionContext(
        user_id=user_id,
        customer_id=1,
        run_id="approval-test-run",
        request_id="approval-test-request",
        permissions=frozenset({"orders:read"}),
        conversation_id=conversation.id,
        db=db,
    )

    result = orchestrator.run(
        "Cancel order",
        context,
        "System prompt",
    )

    assert result.status == "approval_required"
    assert result.error_code == "APPROVAL_REQUIRED"
    assert result.approval_id is not None
    assert executor.calls == []

    approval = db.query(AgentApproval).filter_by(
        approval_id=result.approval_id
    ).one()

    assert approval.status == "pending"
    assert approval.user_id == user_id
    assert approval.conversation_id == conversation.id
    assert approval.run_id == "approval-test-run"
    assert approval.tool_name == "cancel_order"
    assert approval.arguments == {"order_id": "ORD-10025"}
    assert approval.executed_at is None
