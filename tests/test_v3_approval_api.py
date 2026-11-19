
import uuid

import pytest

from app.models.conversation import Conversation
from app.services.v3.approval_service import ApprovalService
from types import SimpleNamespace
from unittest.mock import Mock

from app.api.v3.dependencies import get_agent_service
from app.models.user import User
from app.services.v3.approval_service import approval_service
from app.tools.v3.schemas.results import ToolResult


@pytest.fixture
def pending_approval(db, test_user):
    conversation = Conversation(
        user_id=test_user["id"],
        title="Approval API test",
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    service = ApprovalService()
    approval = service.create_approval(
        db=db,
        run_id="api-approval-run",
        conversation_id=conversation.id,
        user_id=test_user["id"],
        tool_name="cancel_order",
        arguments={"order_id": "ORD-101"},
    )

    return approval


def test_get_approval_api(
    client, auth_headers, pending_approval
):
    response = client.get(
        f"/api/v3/agent/approvals/{pending_approval.approval_id}",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()
    assert data["approval_id"] == pending_approval.approval_id
    assert data["status"] == "pending"
    assert data["tool_name"] == "cancel_order"
    assert data["run_id"] == "api-approval-run"


@pytest.mark.parametrize("decision", ["approved", "rejected"])
def test_confirm_approval_api(
    client, auth_headers, pending_approval, decision
):
    response = client.post(
        f"/api/v3/agent/approvals/{pending_approval.approval_id}/confirm",
        headers=auth_headers,
        json={
            "approval_id": pending_approval.approval_id,
            "decision": decision,
            "reason": "Decision through API test",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["approval_id"] == pending_approval.approval_id
    assert data["status"] == decision
    assert data["decision_reason"] == "Decision through API test"


def test_confirm_approval_rejects_mismatched_id(
    client, auth_headers, pending_approval
):
    response = client.post(
        f"/api/v3/agent/approvals/{pending_approval.approval_id}/confirm",
        headers=auth_headers,
        json={
            "approval_id": "different-approval-id",
            "decision": "approved",
        },
    )

    assert response.status_code == 400

@pytest.fixture
def mock_execution_agent(client, db, test_user):
    user = db.get(User, test_user["id"])

    # Give the test user a valid customer mapping and write permission.
    user.customer_id = user.id
    user.agent_permissions = [
        "orders:read",
        "orders:write",
        "products:read",
        "customers:read",
        "support:write",
        "refunds:read",
    ]
    db.commit()

    real_agent = get_agent_service()

    mock_executor = Mock()
    mock_executor.execute.return_value = ToolResult(
        success=True,
        data={
            "order_id": "ORD-101",
            "status": "cancelled",
        },
    )

    fake_agent = SimpleNamespace(
        registry=real_agent.registry,
        executor=mock_executor,
    )

    client.app.dependency_overrides[get_agent_service] = (
        lambda: fake_agent
    )

    return mock_executor

def test_execute_approved_approval_api(
    client,
    auth_headers,
    pending_approval,
    mock_execution_agent,
):
    # First approve the action.
    confirm_response = client.post(
        f"/api/v3/agent/approvals/{pending_approval.approval_id}/confirm",
        headers=auth_headers,
        json={
            "approval_id": pending_approval.approval_id,
            "decision": "approved",
            "reason": "User approved cancellation",
        },
    )

    assert confirm_response.status_code == 200
    assert confirm_response.json()["status"] == "approved"

    # Then explicitly execute it.
    response = client.post(
        f"/api/v3/agent/approvals/{pending_approval.approval_id}/execute",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "executed"
    assert data["execution_result"]["success"] is True

    mock_execution_agent.execute.assert_called_once()
    
def test_duplicate_execution_is_prevented(
    client,
    auth_headers,
    pending_approval,
    mock_execution_agent,
):
    approval_id = pending_approval.approval_id

    confirm_response = client.post(
        f"/api/v3/agent/approvals/{approval_id}/confirm",
        headers=auth_headers,
        json={
            "approval_id": approval_id,
            "decision": "approved",
        },
    )
    assert confirm_response.status_code == 200

    first_response = client.post(
        f"/api/v3/agent/approvals/{approval_id}/execute",
        headers=auth_headers,
    )
    assert first_response.status_code == 200
    assert first_response.json()["status"] == "executed"

    second_response = client.post(
        f"/api/v3/agent/approvals/{approval_id}/execute",
        headers=auth_headers,
    )

    assert second_response.status_code == 409

    # The sensitive operation must never execute twice.
    mock_execution_agent.execute.assert_called_once()
    
def test_pending_approval_cannot_execute(
    client,
    auth_headers,
    pending_approval,
    mock_execution_agent,
):
    response = client.post(
        f"/api/v3/agent/approvals/{pending_approval.approval_id}/execute",
        headers=auth_headers,
    )

    assert response.status_code == 409
    assert response.json()["detail"].startswith(
        "Approval cannot execute"
    )

    mock_execution_agent.execute.assert_not_called()
       
def test_execution_rechecks_permissions(
    client,
    db,
    auth_headers,
    test_user,
    pending_approval,
    mock_execution_agent,
):
    approval_id = pending_approval.approval_id

    # Approve the action first.
    confirm_response = client.post(
        f"/api/v3/agent/approvals/{approval_id}/confirm",
        headers=auth_headers,
        json={
            "approval_id": approval_id,
            "decision": "approved",
        },
    )
    assert confirm_response.status_code == 200

    # Revoke write permission after approval.
    user = db.get(User, test_user["id"])
    user.agent_permissions = [
        "orders:read",
        "products:read",
        "customers:read",
        "support:write",
        "refunds:read",
    ]
    db.commit()

    response = client.post(
        f"/api/v3/agent/approvals/{approval_id}/execute",
        headers=auth_headers,
    )

    assert response.status_code == 403
    assert "no longer have permission" in response.json()["detail"]

    mock_execution_agent.execute.assert_not_called()
    
def test_another_user_cannot_execute_approval(
    client,
    db,
    pending_approval,
    mock_execution_agent,
):
    email = f"other-{uuid.uuid4().hex[:8]}@example.com"

    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "TestPassword123!",
        },
    )
    assert register_response.status_code in (200, 201)

    # Give the second user a valid, separate customer mapping.
    other_user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )
    other_user.customer_id = other_user.id
    db.commit()

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": "TestPassword123!",
        },
    )
    assert login_response.status_code == 200

    other_headers = {
        "Authorization": (
            f"Bearer {login_response.json()['access_token']}"
        )
    }

    response = client.post(
        f"/api/v3/agent/approvals/{pending_approval.approval_id}/execute",
        headers=other_headers,
    )

    assert response.status_code == 404
    mock_execution_agent.execute.assert_not_called()
    
def test_execution_error_is_recorded_as_unknown(
    client,
    auth_headers,
    pending_approval,
    mock_execution_agent,
):
    approval_id = pending_approval.approval_id

    confirm_response = client.post(
        f"/api/v3/agent/approvals/{approval_id}/confirm",
        headers=auth_headers,
        json={
            "approval_id": approval_id,
            "decision": "approved",
        },
    )
    assert confirm_response.status_code == 200

    mock_execution_agent.execute.return_value = ToolResult(
        success=False,
        error={
            "code": "EXECUTION_ERROR",
            "message": "Tool execution failed.",
        },
    )

    response = client.post(
        f"/api/v3/agent/approvals/{approval_id}/execute",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "execution_unknown"

    mock_execution_agent.execute.assert_called_once()
    

def test_rejected_approval_cannot_execute(
    client,
    auth_headers,
    pending_approval,
    mock_execution_agent,
):
    approval_id = pending_approval.approval_id

    confirm_response = client.post(
        f"/api/v3/agent/approvals/{approval_id}/confirm",
        headers=auth_headers,
        json={
            "approval_id": approval_id,
            "decision": "rejected",
            "reason": "User rejected cancellation",
        },
    )

    assert confirm_response.status_code == 200
    assert confirm_response.json()["status"] == "rejected"

    response = client.post(
        f"/api/v3/agent/approvals/{approval_id}/execute",
        headers=auth_headers,
    )

    assert response.status_code == 409
    mock_execution_agent.execute.assert_not_called()
