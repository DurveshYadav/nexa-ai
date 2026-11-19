
from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from app.api.v3.schemas.approvals import (
    ApprovalRequest,
    ApprovalDecision,
    ApprovalResponse,
)


def test_valid_approval_request():
    now = datetime.now(timezone.utc)

    request = ApprovalRequest(
        approval_id="APR-1001",
        run_id="run-123",
        conversation_id=1,
        tool_name="cancel_order",
        status="pending",
        created_at=now,
        expires_at=now + timedelta(minutes=15),
    )

    assert request.approval_id == "APR-1001"
    assert request.conversation_id == 1
    assert request.status == "pending"


def test_invalid_approval_status():
    now = datetime.now(timezone.utc)

    with pytest.raises(ValidationError):
        ApprovalRequest(
            approval_id="APR-1001",
            run_id="run-123",
            conversation_id=1,
            tool_name="cancel_order",
            status="invalid",
            created_at=now,
            expires_at=now + timedelta(minutes=15),
        )


def test_valid_approval_decision():
    decision = ApprovalDecision(
        approval_id="APR-1001",
        decision="approved",
        reason="User confirmed",
    )

    assert decision.decision == "approved"


def test_invalid_approval_decision():
    with pytest.raises(ValidationError):
        ApprovalDecision(
            approval_id="APR-1001",
            decision="maybe",
        )
