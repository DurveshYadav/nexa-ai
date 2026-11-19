from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


AgentRunStatus = Literal[
    "pending",
    "running",
    "waiting_for_approval",
    "completed",
    "failed",
    "cancelled",
]


class AgentRunState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str = Field(min_length=1)
    user_id: int = Field(gt=0)

    status: AgentRunStatus = "pending"

    iteration: int = Field(default=0, ge=0)
    tool_calls_count: int = Field(default=0, ge=0)

    current_tool: str | None = None
    error_code: str | None = None

