
from typing import Literal

from pydantic import Field

from app.tools.v3.schemas.common import BaseSchema


class AgentChatRequest(BaseSchema):
    message: str = Field(min_length=1, max_length=5000)
    conversation_id: int | None = Field(default=None, gt=0)


class AgentChatResponse(BaseSchema):
    run_id: str = Field(min_length=1)
    conversation_id: int = Field(gt=0)
    status: Literal["completed", "failed", "approval_required"]
    message: str = Field(min_length=1)
    approval_id: str | None = None
