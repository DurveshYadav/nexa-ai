from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


ExecutionStepStatus = Literal[
    "pending",
    "running",
    "completed",
    "failed",
]


class ExecutionStep(BaseModel):
    model_config = ConfigDict(extra="forbid")

    step_number: int = Field(ge=1)
    tool_call_id: str = Field(min_length=1)
    tool_name: str = Field(min_length=1)

    status: ExecutionStepStatus = "pending"

    error_code: str | None = None
    duration_ms: float | None = Field(default=None, ge=0)
