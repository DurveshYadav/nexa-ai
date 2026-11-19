
from app.tools.v3.registry import ToolRegistry, ToolSpec
from app.tools.v3.executor import ToolExecutor
from app.tools.v3.dependencies import ToolDependencies
from app.tools.v3.context import ExecutionContext

from app.tools.v3.schemas.common import BaseSchema
from app.tools.v3.schemas.results import ToolResult, ToolError


class ValidOutput(BaseSchema):
    order_id: str
    status: str


def valid_handler(arguments, context):
    return ToolResult(
        success=True,
        data={
            "order_id": "ORD-10025",
            "status": "shipped",
        },
    )


def invalid_handler(arguments, context):
    return ToolResult(
        success=True,
        data={
            "order_id": "ORD-10025",
            "unexpected_field": "invalid",
        },
    )


def build_executor(handler):
    registry = ToolRegistry()

    registry.register(
        ToolSpec(
            name="test_tool",
            description="Test output validation",
            input_schema=ValidOutput,
            handler=handler,
            output_schema=ValidOutput,
        )
    )

    return ToolExecutor(
        registry=registry,
        dependencies=ToolDependencies(),
    )


def test_valid_tool_output():
    executor = build_executor(valid_handler)

    result = executor.execute(
        "test_tool",
        {
            "order_id": "ORD-10025",
            "status": "shipped",
        },
        ExecutionContext(1, 1, "run-1", "req-1"),
    )

    assert result.success is True
    assert result.data["status"] == "shipped"


def test_invalid_tool_output():
    executor = build_executor(invalid_handler)

    result = executor.execute(
        "test_tool",
        {
            "order_id": "ORD-10025",
            "status": "shipped",
        },
        ExecutionContext(1, 1, "run-1", "req-1"),
    )

    assert result.success is False
    assert result.error.code == "INVALID_TOOL_OUTPUT"
