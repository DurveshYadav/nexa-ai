
from pydantic import Field

from app.tools.v3.schemas.common import BaseSchema


class ToolError(BaseSchema):
    code: str = Field(min_length=1)
    message: str = Field(min_length=1)


class ToolResult(BaseSchema):
    success: bool
    data: dict | None = None
    error: ToolError | None = None


class OrderStatusData(BaseSchema):
    order_id: str
    status: str
    tracking_number: str | None = None


class OrderDetailsData(BaseSchema):
    order_id: str
    status: str
    tracking_number: str | None = None
    total_amount: float
    items: list[dict]


class CancelOrderData(BaseSchema):
    order_id: str
    status: str
    message: str


class ProductDetailsData(BaseSchema):
    product_id: str
    product_name: str
    description: str
    price: float
    available_quantity: int


class ProductAvailabilityData(BaseSchema):
    product_id: str
    available: bool
    available_quantity: int


class CustomerProfileData(BaseSchema):
    customer_id: int
    name: str
    email: str
    phone: str


class SupportTicketData(BaseSchema):
    ticket_id: str
    customer_id: int
    subject: str
    description: str
    status: str
