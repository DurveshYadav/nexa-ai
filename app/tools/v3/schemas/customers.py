
from pydantic import Field
from app.tools.v3.schemas.common import BaseSchema

class GetCustomerProfileInput(BaseSchema):
        pass
    # customer_id: str = Field(
    #     min_length=5,
    #     max_length=30,
    #     pattern=r"^CUST-[A-Za-z0-9-]+$",
    # )

