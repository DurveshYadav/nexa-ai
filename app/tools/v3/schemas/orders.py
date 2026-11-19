
from pydantic import Field

from app.tools.v3.schemas.common import BaseSchema


class GetOrderStatusInput(BaseSchema):
    order_id: str = Field(
        min_length=5,
        max_length=30,
        pattern=r"^ORD-[A-Za-z0-9-]+$",
    )


class GetOrderDetailsInput(BaseSchema):
    order_id: str = Field(
        min_length=5,
        max_length=30,
        pattern=r"^ORD-[A-Za-z0-9-]+$",
    )


class CancelOrderInput(BaseSchema):
    order_id: str = Field(
        min_length=5,
        max_length=30,
        pattern=r"^ORD-[A-Za-z0-9-]+$",
    )
