
from datetime import datetime
from typing import Literal

from pydantic import Field

from app.tools.v3.schemas.common import BaseSchema


ApprovalStatus = Literal[
    "pending",
    "approved",
    "rejected",
    "expired",
    "cancelled",
    "executing",
    "executed",
    "execution_failed",
    "execution_unknown",
]

class ApprovalRequest(BaseSchema):
    approval_id: str = Field(min_length=1)
    run_id: str = Field(min_length=1)
    conversation_id: int
    tool_name: str = Field(min_length=1)
    status: ApprovalStatus
    created_at: datetime
    expires_at: datetime


class ApprovalDecision(BaseSchema):
    approval_id: str = Field(min_length=1)
    decision: Literal["approved", "rejected"]
    reason: str | None = Field(default=None, max_length=500)


class ApprovalResponse(BaseSchema):
    approval_id: str
    run_id: str
    conversation_id: int
    tool_name: str
    status: ApprovalStatus
    created_at: datetime
    expires_at: datetime
    approved_at: datetime | None = None
    rejected_at: datetime | None = None
    executed_at: datetime | None = None
    decision_reason: str | None = None
    execution_result: dict | None = None
