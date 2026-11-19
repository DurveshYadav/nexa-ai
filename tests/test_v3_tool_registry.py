
import pytest

from app.tools.v3.registry import ToolRegistry, ToolSpec
from app.tools.v3.schemas.orders import GetOrderStatusInput
from app.tools.v3.handlers.orders import get_order_status_handler


@pytest.fixture
def tool_spec():
    return ToolSpec(
        name="get_order_status",
        description="Get authenticated customer's order status.",
        input_schema=GetOrderStatusInput,
        handler=get_order_status_handler,
        enabled=True,
        permission="orders:read",
    )


def test_register_and_get_tool(tool_spec):
    registry = ToolRegistry()

    registry.register(tool_spec)

    result = registry.get("get_order_status")

    assert result.name == "get_order_status"
    assert result.handler is get_order_status_handler


def test_unknown_tool():
    registry = ToolRegistry()

    with pytest.raises(ValueError, match="Unknown tool"):
        registry.get("unknown_tool")


def test_duplicate_tool_registration(tool_spec):
    registry = ToolRegistry()

    registry.register(tool_spec)

    with pytest.raises(ValueError, match="already registered"):
        registry.register(tool_spec)


def test_list_registered_tools(tool_spec):
    registry = ToolRegistry()

    registry.register(tool_spec)

    tools = registry.list_tools()

    assert len(tools) == 1
    assert tools[0].name == "get_order_status"
