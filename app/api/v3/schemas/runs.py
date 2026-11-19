from pydantic import BaseModel, ConfigDict


class AgentRunResponse(BaseModel):
    run_id: str
    status: str
    iteration: int
    tool_calls_count: int
    current_tool: str | None = None
    error_code: str | None = None


class ExecutionStepResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    step_number: int
    tool_call_id: str
    tool_name: str
    status: str
    error_code: str | None = None
    duration_ms: float | None = None


class AgentRunHistoryResponse(BaseModel):
    run_id: str
    steps: list[ExecutionStepResponse]
