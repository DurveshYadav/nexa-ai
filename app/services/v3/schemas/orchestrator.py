from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class OrchestratorResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["completed", "failed", "approval_required"]
    content: str = Field(min_length=1)
    iterations: int = Field(ge=0)
    tool_calls_count: int = Field(ge=0)
    error_code: str | None = None
    approval_id: str | None = None
