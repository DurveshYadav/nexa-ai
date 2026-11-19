from app.services.v3.schemas.agent_state import AgentRunState
from app.services.v3.schemas.execution import ExecutionStep


class AgentRunManager:

    def __init__(self):
        self.runs: dict[str, AgentRunState] = {}
        self.history: dict[str, list[ExecutionStep]] = {}

    def create_run(
        self,
        run_id: str,
        user_id: int,
    ) -> AgentRunState:

        if run_id in self.runs:
            raise ValueError("Run already exists")

        state = AgentRunState(
            run_id=run_id,
            user_id=user_id,
        )

        self.runs[run_id] = state
        self.history[run_id] = []

        return state

    def get_run(
        self,
        run_id: str,
        user_id: int,
    ) -> AgentRunState:

        state = self.runs.get(run_id)

        if state is None or state.user_id != user_id:
            raise ValueError("Run not found")

        return state

    def update_status(
        self,
        run_id: str,
        user_id: int,
        status: str,
        error_code: str | None = None,
    ) -> AgentRunState:

        state = self.get_run(run_id, user_id)

        state.status = status
        state.error_code = error_code

        return state

    def update_progress(
        self,
        run_id: str,
        user_id: int,
        iteration: int,
        tool_calls_count: int,
        current_tool: str | None = None,
    ) -> AgentRunState:

        state = self.get_run(run_id, user_id)

        state.iteration = iteration
        state.tool_calls_count = tool_calls_count
        state.current_tool = current_tool

        return state

    def add_step(
        self,
        run_id: str,
        user_id: int,
        step: ExecutionStep,
    ) -> ExecutionStep:

        self.get_run(run_id, user_id)
        self.history[run_id].append(step)

        return step

    def get_history(
        self,
        run_id: str,
        user_id: int,
    ) -> list[ExecutionStep]:

        self.get_run(run_id, user_id)

        return list(self.history[run_id])

    def cancel_run(
        self,
        run_id: str,
        user_id: int,
    ) -> AgentRunState:

        state = self.get_run(run_id, user_id)

        if state.status not in {"pending", "running"}:
            raise ValueError("Run cannot be cancelled")

        state.status = "cancelled"
        state.current_tool = None

        return state
