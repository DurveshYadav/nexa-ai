import pytest

from app.services.v3.run_manager import AgentRunManager
from app.services.v3.schemas.execution import ExecutionStep


@pytest.fixture
def manager():
    return AgentRunManager()


def test_create_and_get_run(manager):
    state = manager.create_run("run-1", user_id=1)

    assert state.run_id == "run-1"
    assert state.user_id == 1
    assert state.status == "pending"

    retrieved = manager.get_run("run-1", user_id=1)
    assert retrieved.run_id == "run-1"


def test_prevent_duplicate_run(manager):
    manager.create_run("run-1", user_id=1)

    with pytest.raises(ValueError):
        manager.create_run("run-1", user_id=1)


def test_prevent_cross_user_access(manager):
    manager.create_run("run-1", user_id=1)

    with pytest.raises(ValueError):
        manager.get_run("run-1", user_id=2)


def test_update_run_progress(manager):
    manager.create_run("run-1", user_id=1)

    state = manager.update_progress(
        run_id="run-1",
        user_id=1,
        iteration=2,
        tool_calls_count=3,
        current_tool="get_order_status",
    )

    assert state.iteration == 2
    assert state.tool_calls_count == 3
    assert state.current_tool == "get_order_status"


def test_add_and_get_execution_history(manager):
    manager.create_run("run-1", user_id=1)

    step = ExecutionStep(
        step_number=1,
        tool_call_id="call-1",
        tool_name="get_order_status",
        status="completed",
        duration_ms=10.5,
    )

    manager.add_step("run-1", 1, step)

    history = manager.get_history("run-1", 1)

    assert len(history) == 1
    assert history[0].tool_name == "get_order_status"


def test_cancel_running_run(manager):
    manager.create_run("run-1", user_id=1)
    manager.update_status("run-1", 1, "running")

    state = manager.cancel_run("run-1", 1)

    assert state.status == "cancelled"
    assert state.current_tool is None


def test_cannot_cancel_completed_run(manager):
    manager.create_run("run-1", user_id=1)
    manager.update_status("run-1", 1, "completed")

    with pytest.raises(ValueError):
        manager.cancel_run("run-1", 1)
