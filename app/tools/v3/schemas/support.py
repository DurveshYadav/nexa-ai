
from pydantic import Field

from app.tools.v3.schemas.common import BaseSchema


class CreateSupportTicketInput(BaseSchema):
    subject: str = Field(min_length=5, max_length=150)
    description: str = Field(min_length=10, max_length=2000)


class SupportTicketData(BaseSchema):
    ticket_id: str = Field(min_length=1)
    customer_id: int = Field(gt=0)
    subject: str = Field(min_length=1)
    status: str = Field(min_length=1)
