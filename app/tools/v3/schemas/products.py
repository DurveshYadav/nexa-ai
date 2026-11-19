# from pydantic import BaseModel, ConfigDict, Field
from pydantic import Field
from app.tools.v3.schemas.common import BaseSchema

class GetProductDetailsInput(BaseSchema):
    product_id: str = Field(
        min_length=5,
        max_length=30,
        pattern=r"^PROD-[A-Za-z0-9-]+$",
    )

class CheckProductAvailabilityInput(BaseSchema):
    product_id: str = Field(
        min_length=5,
        max_length=30,
        pattern=r"^PROD-[A-Za-z0-9-]+$",
    )
