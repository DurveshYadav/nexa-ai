from app.services.v3.customer_service import CustomerService
from app.services.v3.order_service import OrderService
from app.services.v3.refund_service import RefundService
from app.services.v3.support_service import SupportService
from app.tools.v3.context import ExecutionContext
from app.tools.v3.handlers.customers import get_customer_profile_handler
from app.tools.v3.handlers.support import create_support_ticket_handler
from app.tools.v3.handlers.refunds import (
    check_refund_eligibility_handler,
    request_refund_handler,
)
from app.tools.v3.schemas.support import CreateSupportTicketInput
from app.tools.v3.schemas.refunds import (
    CheckRefundEligibilityInput,
    RequestRefundInput,
)


def test_customer_profile_success():
    result = get_customer_profile_handler(
        ExecutionContext(1, 1, "run-1", "req-1"),
        CustomerService(),
    )
    assert result.success is True
    assert result.data["customer_id"] == 1


def test_customer_profile_not_found():
    result = get_customer_profile_handler(
        ExecutionContext(1, 999, "run-1", "req-1"),
        CustomerService(),
    )
    assert result.success is False
    assert result.error.code == "CUSTOMER_NOT_FOUND"


def test_create_support_ticket():
    result = create_support_ticket_handler(
        CreateSupportTicketInput(
            subject="Order issue",
            description="My order has not arrived",
        ),
        ExecutionContext(1, 1, "run-1", "req-1"),
        SupportService(),
    )
    assert result.success is True
    assert result.data["ticket_id"] == "TKT-1001"
    assert result.data["customer_id"] == 1


def test_refund_not_found():
    result = check_refund_eligibility_handler(
        CheckRefundEligibilityInput(order_id="ORD-99999"),
        ExecutionContext(1, 1, "run-1", "req-1"),
        RefundService(),
        OrderService(),
    )
    assert result.success is False
    assert result.error.code == "ORDER_NOT_FOUND"


def test_refund_not_eligible():
    result = check_refund_eligibility_handler(
        CheckRefundEligibilityInput(order_id="ORD-10025"),
        ExecutionContext(1, 1, "run-1", "req-1"),
        RefundService(),
        OrderService(),
    )
    assert result.success is False
    assert result.error.code == "REFUND_NOT_ELIGIBLE"


def test_refund_request_success():
    order_service = OrderService()
    order_service.orders["ORD-10025"]["status"] = "delivered"

    result = request_refund_handler(
        RequestRefundInput(order_id="ORD-10025"),
        ExecutionContext(1, 1, "run-1", "req-1"),
        RefundService(),
        order_service,
    )
    assert result.success is True
    assert result.data["eligible"] is True
    assert result.data["message"] == "Refund request submitted."

