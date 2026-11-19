
from pydantic import Field

from app.tools.v3.schemas.common import BaseSchema


class CheckRefundEligibilityInput(BaseSchema):
    order_id: str = Field(
        min_length=5,
        max_length=30,
        pattern=r"^ORD-[A-Za-z0-9-]+$",
    )


class RequestRefundInput(BaseSchema):
    order_id: str = Field(
        min_length=5,
        max_length=30,
        pattern=r"^ORD-[A-Za-z0-9-]+$",
    )


class RefundData(BaseSchema):
    order_id: str = Field(
        min_length=5,
        max_length=30,
        pattern=r"^ORD-[A-Za-z0-9-]+$",
    )
    eligible: bool
    status: str = Field(min_length=1)
    message: str = Field(min_length=1)
