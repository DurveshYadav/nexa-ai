
from app.integrations.llm.schemas import LLMResponse, LLMToolCall
from app.services.v3.agent_service import AgentService
from app.tools.v3.context import ExecutionContext
from app.tools.v3.schemas.results import ToolResult


class FakeProvider:

    def __init__(self, responses):
        self.responses = responses
        self.calls = []

    def generate(self, messages, tools=None):
        self.calls.append({
            "messages": messages.copy(),
            "tools": tools,
        })
        return self.responses.pop(0)


def make_context(permissions=frozenset()):
    return ExecutionContext(
        user_id=1,
        customer_id=1,
        run_id="run-1",
        request_id="req-1",
        permissions=permissions,
    )


def test_agent_returns_normal_llm_response():
    provider = FakeProvider([
        LLMResponse(
            content="Hello! How can I help?",
            model="gpt-5-mini",
        )
    ])

    service = AgentService(provider=provider)

    result = service.chat(
        "Hello",
        make_context(),
    )

    assert result == "Hello! How can I help?"
    assert len(provider.calls) == 1


def test_agent_executes_tool_and_returns_final_response(monkeypatch):
    provider = FakeProvider([
        LLMResponse(
            content=None,
            model="gpt-5-mini",
            tool_calls=[
                LLMToolCall(
                    id="call_123",
                    name="get_order_status",
                    arguments={"order_id": "ORD-10025"},
                )
            ],
        ),
        LLMResponse(
            content="Your order has been shipped.",
            model="gpt-5-mini",
        ),
    ])

    service = AgentService(provider=provider)

    executed = []

    def mock_execute(tool_name, arguments, context):
        executed.append((tool_name, arguments, context))
        return ToolResult(
            success=True,
            data={"order_id": "ORD-10025", "status": "shipped"},
        )

    monkeypatch.setattr(service.executor, "execute", mock_execute)

    result = service.chat(
        "Check my order",
        make_context(frozenset({"orders:read"})),
    )

    assert result == "Your order has been shipped."
    assert len(executed) == 1
    assert executed[0][0] == "get_order_status"
    assert executed[0][1] == {"order_id": "ORD-10025"}
    assert executed[0][2].user_id == 1

    final_messages = provider.calls[1]["messages"]
    assert final_messages[-1]["role"] == "tool"
    assert final_messages[-1]["tool_call_id"] == "call_123"

def test_agent_blocks_sensitive_tool(monkeypatch):
    provider = FakeProvider([
        LLMResponse(
            content=None,
            model="gpt-5-mini",
            tool_calls=[
                LLMToolCall(
                    id="call_456",
                    name="cancel_order",
                    arguments={"order_id": "ORD-10025"},
                )
            ],
        ),
    ])

    service = AgentService(provider=provider)

    def should_not_execute(**kwargs):
        raise AssertionError("Sensitive tool must not execute")

    monkeypatch.setattr(
        service.executor,
        "execute",
        should_not_execute,
    )

    result = service.chat(
        "Cancel my order",
        make_context(frozenset({"orders:write"})),
    )

    assert "Approval could not be created" in result
    assert len(provider.calls) == 1

def test_agent_enforces_max_tool_iterations():
    provider = FakeProvider([
        LLMResponse(
            content=None,
            model="gpt-5-mini",
            tool_calls=[
                LLMToolCall(
                    id="call_1",
                    name="get_order_status",
                    arguments={"order_id": "ORD-10025"},
                )
            ],
        ),
        LLMResponse(
            content=None,
            model="gpt-5-mini",
            tool_calls=[
                LLMToolCall(
                    id="call_2",
                    name="get_order_status",
                    arguments={"order_id": "ORD-10025"},
                )
            ],
        ),
    ])

    service = AgentService(
        provider=provider,
        max_tool_iterations=1,
    )

    result = service.chat(
        "Check my order",
        make_context(frozenset({"orders:read"})),
    )

    assert "maximum orchestration iterations" in result
    assert len(provider.calls) == 1


def test_agent_respects_backend_permission(monkeypatch):
    provider = FakeProvider([
        LLMResponse(
            content=None,
            model="gpt-5-mini",
            tool_calls=[
                LLMToolCall(
                    id="call_789",
                    name="get_order_status",
                    arguments={"order_id": "ORD-10025"},
                )
            ],
        ),
        LLMResponse(
            content="You do not have permission to access this order.",
            model="gpt-5-mini",
        ),
    ])

    service = AgentService(provider=provider)

    def mock_execute(tool_name, arguments, context):
        assert "orders:read" not in context.permissions

        return ToolResult(
            success=False,
            error={
                "code": "PERMISSION_DENIED",
                "message": "You do not have permission to execute this tool.",
            },
        )

    monkeypatch.setattr(service.executor, "execute", mock_execute)

    result = service.chat(
        "Check my order",
        make_context(),
    )

    assert "permission" in result.lower()
    assert len(provider.calls) == 2
