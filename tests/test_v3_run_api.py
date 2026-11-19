from types import SimpleNamespace

from app.api.v3.dependencies import get_agent_service
from app.models.user import User
from app.services.v3.run_manager import AgentRunManager
from app.services.v3.schemas.execution import ExecutionStep


def test_v3_run_requires_authentication(client):
    response = client.get("/api/v3/agent/runs/test-run")

    assert response.status_code == 401


def test_v3_run_status_and_history(
    client,
    db,
    test_user,
    auth_headers,
):
    user = db.query(User).filter(
        User.email == test_user["email"]
    ).first()

    run_manager = AgentRunManager()
    run_manager.create_run("test-run-123", user.id)
    run_manager.update_status(
        "test-run-123",
        user.id,
        "completed",
    )
    run_manager.update_progress(
        "test-run-123",
        user.id,
        iteration=2,
        tool_calls_count=1,
        current_tool="get_order_status",
    )
    run_manager.add_step(
        "test-run-123",
        user.id,
        ExecutionStep(
            step_number=1,
            tool_call_id="call-123",
            tool_name="get_order_status",
            status="completed",
            duration_ms=25.5,
        ),
    )

    fake_service = SimpleNamespace(
        orchestrator=SimpleNamespace(
            run_manager=run_manager,
        )
    )

    overrides = client.app.dependency_overrides
    overrides[get_agent_service] = lambda: fake_service

    try:
        status_response = client.get(
            "/api/v3/agent/runs/test-run-123",
            headers=auth_headers,
        )

        history_response = client.get(
            "/api/v3/agent/runs/test-run-123/history",
            headers=auth_headers,
        )
    finally:
        overrides.pop(get_agent_service, None)

    assert status_response.status_code == 200
    assert status_response.json()["status"] == "completed"
    assert status_response.json()["iteration"] == 2
    assert status_response.json()["tool_calls_count"] == 1

    assert history_response.status_code == 200
    assert len(history_response.json()["steps"]) == 1
    assert history_response.json()["steps"][0]["tool_name"] == (
        "get_order_status"
    )


def test_v3_run_cannot_be_accessed_by_another_user(
    client,
    db,
    test_user,
    auth_headers,
):
    user = db.query(User).filter(
        User.email == test_user["email"]
    ).first()

    run_manager = AgentRunManager()
    run_manager.create_run("private-run-123", user.id + 1)

    fake_service = SimpleNamespace(
        orchestrator=SimpleNamespace(
            run_manager=run_manager,
        )
    )

    overrides = client.app.dependency_overrides
    overrides[get_agent_service] = lambda: fake_service

    try:
        response = client.get(
            "/api/v3/agent/runs/private-run-123",
            headers=auth_headers,
        )
    finally:
        overrides.pop(get_agent_service, None)

    assert response.status_code == 404
