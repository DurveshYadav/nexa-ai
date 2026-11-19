
import pytest
from pydantic import ValidationError

from app.tools.v3.schemas.orders import GetOrderStatusInput
from app.tools.v3.schemas.products import GetProductDetailsInput
from app.tools.v3.schemas.support import CreateSupportTicketInput
from app.tools.v3.schemas.refunds import RequestRefundInput


def test_valid_order_input():
    assert GetOrderStatusInput(
        order_id="ORD-10025"
    ).order_id == "ORD-10025"


def test_invalid_order_input():
    with pytest.raises(ValidationError):
        GetOrderStatusInput(order_id="INVALID")


def test_valid_product_input():
    assert GetProductDetailsInput(
        product_id="PROD-101"
    ).product_id == "PROD-101"


def test_invalid_support_ticket():
    with pytest.raises(ValidationError):
        CreateSupportTicketInput(
            subject="Hi",
            description="Short",
        )


def test_valid_refund_input():
    assert RequestRefundInput(
        order_id="ORD-10025"
    ).order_id == "ORD-10025"
