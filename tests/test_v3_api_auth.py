from uuid import uuid4

from app.api.v3.endpoints.agent import get_agent_service
from app.models.user import User
from app.services.conversation_service import conversation_service
from app.services.v3.schemas.orchestrator import OrchestratorResult


class FakeAgentService:
    def run(self, message, context):
        assert context.user_id > 0
        # assert context.customer_id == 1001
        assert context.customer_id == 900000 + context.user_id
        assert "orders:read" in context.permissions

        return OrchestratorResult(
            status="completed",
            content="Your order is shipped.",
            iterations=1,
            tool_calls_count=1,
        )


def test_v3_agent_requires_authentication(client):
    response = client.post(
        "/api/v3/agent/chat",
        json={"message": "Check my order"},
    )

    assert response.status_code == 401


def test_v3_agent_requires_customer_mapping(
    client,
    db,
    test_user,
    auth_headers,
):
    user = db.query(User).filter(
        User.email == test_user["email"]
    ).first()

    assert user is not None
    assert user.customer_id is None

    response = client.post(
        "/api/v3/agent/chat",
        headers=auth_headers,
        json={"message": "Check my order"},
    )

    assert response.status_code == 403


def test_v3_agent_cannot_access_another_users_conversation(
    client,
    db,
    test_user,
    auth_headers,
):
    user_a = db.query(User).filter(
        User.email == test_user["email"]
    ).first()

    other_email = f"other-{uuid4().hex[:8]}@example.com"

    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": other_email,
            "password": "TestPassword123!",
        },
    )
    assert register_response.status_code in (200, 201)

    user_b = db.query(User).filter(
        User.email == other_email
    ).first()

    conversation = conversation_service.create_conversation(
        db=db,
        user_id=user_b.id,
        title="Another user's conversation",
    )

    user_a.customer_id = 1001
    db.commit()

    response = client.post(
        "/api/v3/agent/chat",
        headers=auth_headers,
        json={
            "message": "Check my order",
            "conversation_id": conversation.id,
        },
    )

    assert response.status_code == 404


def test_v3_agent_can_use_own_conversation(
    client,
    db,
    test_user,
    auth_headers,
):
    user = db.query(User).filter(
        User.email == test_user["email"]
    ).first()

    # user.customer_id = 1001
    user.customer_id = 900000 + user.id
    db.commit()

    conversation = conversation_service.create_conversation(
        db=db,
        user_id=user.id,
        title="My support conversation",
    )

    app_overrides = client.app.dependency_overrides
    app_overrides[get_agent_service] = FakeAgentService

    try:
        response = client.post(
            "/api/v3/agent/chat",
            headers=auth_headers,
            json={
                "message": "Check my order",
                "conversation_id": conversation.id,
            },
        )
    finally:
        app_overrides.pop(get_agent_service, None)

    assert response.status_code == 200

    data = response.json()
    assert data["conversation_id"] == conversation.id
    assert data["status"] == "completed"
    assert data["message"] == "Your order is shipped."
    assert data["run_id"]

class FakeApprovalAgentService:
    def run(self, message, context):
        assert context.user_id > 0
        assert context.conversation_id is not None
        assert context.db is not None

        return OrchestratorResult(
            status="approval_required",
            content="Your approval is required before this action can proceed.",
            iterations=1,
            tool_calls_count=0,
            error_code="APPROVAL_REQUIRED",
            approval_id="test-approval-123",
        )

def test_v3_agent_returns_approval_id(
    client,
    db,
    test_user,
    auth_headers,
):
    user = db.query(User).filter(
        User.email == test_user["email"]
    ).first()

    user.customer_id = 900000 + user.id
    db.commit()

    app_overrides = client.app.dependency_overrides
    app_overrides[get_agent_service] = FakeApprovalAgentService

    try:
        response = client.post(
            "/api/v3/agent/chat",
            headers=auth_headers,
            json={"message": "Cancel my order"},
        )
    finally:
        app_overrides.pop(get_agent_service, None)

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "approval_required"
    assert data["approval_id"] == "test-approval-123"
    assert data["message"] == (
        "Your approval is required before this action can proceed."
    )
    assert data["conversation_id"] > 0
    assert data["run_id"]
