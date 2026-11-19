
from app.tools.v3.registration import build_tool_registry
from app.tools.v3.executor import ToolExecutor
from app.tools.v3.dependencies import ToolDependencies
from app.tools.v3.context import ExecutionContext


def make_executor():
    return ToolExecutor(
        build_tool_registry(),
        ToolDependencies(),
    )


def make_context(*permissions):
    return ExecutionContext(
        user_id=1,
        customer_id=1,
        run_id="run-test",
        request_id="req-test",
        permissions=frozenset(permissions),
    )


def test_get_order_status_success():
    executor = make_executor()
    context = make_context("orders:read")

    result = executor.execute(
        "get_order_status",
        {"order_id": "ORD-10025"},
        context,
    )

    assert result.success is True
    assert result.data["status"] == "shipped"


def test_unknown_tool():
    result = make_executor().execute(
        "unknown_tool",
        {},
        make_context(),
    )

    assert result.success is False
    assert result.error.code == "UNKNOWN_TOOL"


def test_invalid_arguments():
    result = make_executor().execute(
        "get_order_status",
        {"wrong_field": "value"},
        make_context("orders:read"),
    )

    assert result.success is False
    assert result.error.code == "INVALID_ARGUMENTS"


def test_permission_denied():
    result = make_executor().execute(
        "get_order_status",
        {"order_id": "ORD-10025"},
        make_context(),
    )

    assert result.success is False
    assert result.error.code == "PERMISSION_DENIED"


def test_customer_profile_success():
    result = make_executor().execute(
        "get_customer_profile",
        {},
        make_context("customers:read"),
    )

    assert result.success is True
    assert result.data["customer_id"] == 1


def test_product_details_success():
    result = make_executor().execute(
        "get_product_details",
        {"product_id": "PROD-101"},
        make_context("products:read"),
    )

    assert result.success is True


def test_disabled_tool():
    from dataclasses import replace

    registry = build_tool_registry()
    original = registry.get("get_order_status")

    registry._tools["get_order_status"] = replace(
        original,
        enabled=False,
    )

    result = ToolExecutor(
        registry,
        ToolDependencies(),
    ).execute(
        "get_order_status",
        {"order_id": "ORD-10025"},
        make_context("orders:read"),
    )

    assert result.success is False
    assert result.error.code == "TOOL_DISABLED"

def test_handler_exception():
    from dataclasses import replace

    registry = build_tool_registry()
    original = registry.get("get_order_status")

    def failing_handler(**kwargs):
        raise RuntimeError("Internal test exception")

    registry._tools["get_order_status"] = replace(
        original,
        handler=failing_handler,
    )

    executor = ToolExecutor(registry, ToolDependencies())

    result = executor.execute(
        "get_order_status",
        {"order_id": "ORD-10025"},
        make_context("orders:read"),
    )

    assert result.success is False
    assert result.error.code == "EXECUTION_ERROR"

