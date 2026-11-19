import pytest
from pydantic import ValidationError

from app.tools.v3.context import ExecutionContext
from app.services.v3.order_service import OrderService
from app.tools.v3.schemas.orders import GetOrderStatusInput, GetOrderDetailsInput, CancelOrderInput
from app.tools.v3.handlers.orders import (
    get_order_status_handler,
    get_order_details_handler,
    cancel_order_handler,
)

def test_get_order_status_success():
    result = get_order_status_handler(
        GetOrderStatusInput(order_id="ORD-10025"),
        ExecutionContext(1, 1, "run-1", "req-1"),
        OrderService(),
    )

    assert result.success is True
    assert result.data["status"] == "shipped"


def test_get_order_status_other_customer_denied():
    result = get_order_status_handler(
        GetOrderStatusInput(order_id="ORD-10025"),
        ExecutionContext(2, 2, "run-2", "req-2"),
        OrderService(),
    )

    assert result.success is False
    assert result.error.code == "ORDER_NOT_FOUND"


def test_invalid_order_id_rejected():
    with pytest.raises(ValidationError):
        GetOrderStatusInput(order_id="INVALID-123")

def test_get_order_details_success():
    result = get_order_details_handler(
        GetOrderDetailsInput(order_id="ORD-10025"),
        ExecutionContext(1, 1, "run-1", "req-1"),
        OrderService(),
    )

    assert result.success is True
    assert result.data["total_amount"] == 2499.0
    assert len(result.data["items"]) == 1


def test_get_order_details_other_customer_denied():
    result = get_order_details_handler(
        GetOrderDetailsInput(order_id="ORD-10025"),
        ExecutionContext(2, 2, "run-2", "req-2"),
        OrderService(),
    )

    assert result.success is False
    assert result.error.code == "ORDER_NOT_FOUND"

def test_cancel_pending_order_success():
    result = cancel_order_handler(
        CancelOrderInput(order_id="ORD-10026"),
        ExecutionContext(1, 1, "run-1", "req-1"),
        OrderService(),
    )

    assert result.success is True
    assert result.data["status"] == "cancelled"


def test_cancel_shipped_order_rejected():
    result = cancel_order_handler(
        CancelOrderInput(order_id="ORD-10025"),
        ExecutionContext(1, 1, "run-1", "req-1"),
        OrderService(),
    )

    assert result.success is False
    assert result.error.code == "ORDER_CANNOT_BE_CANCELLED"


def test_cancel_other_customers_order_denied():
    result = cancel_order_handler(
        CancelOrderInput(order_id="ORD-10026"),
        ExecutionContext(2, 2, "run-2", "req-2"),
        OrderService(),
    )

    assert result.success is False
    assert result.error.code == "ORDER_NOT_FOUND"

def test_cancel_order_status_persists():
    service = OrderService()

    service.cancel_order("ORD-10026", 1)

    result = service.get_order_status("ORD-10026", 1)

    assert result["status"] == "cancelled"

