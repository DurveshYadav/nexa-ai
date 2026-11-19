import pytest

from app.models.conversation import Conversation
from app.services.v3.approval_service import ApprovalService
from app.repositories.approval_repository import approval_repository


@pytest.fixture
def approval_service():
    return ApprovalService()


@pytest.fixture
def test_conversation(db, test_user):
    conversation = Conversation(
        user_id=test_user["id"],
        title="Approval test conversation",
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation


def test_create_sensitive_tool_approval(
    db, test_user, test_conversation, approval_service
):
    approval = approval_service.create_approval(
        db=db,
        run_id="run-approval-1",
        conversation_id=test_conversation.id,
        user_id=test_user["id"],
        tool_name="cancel_order",
        arguments={"order_id": "ORD-101"},
    )

    assert approval.status == "pending"
    assert approval.tool_name == "cancel_order"
    assert approval.arguments == {"order_id": "ORD-101"}
    assert approval.user_id == test_user["id"]
    assert approval.expires_at is not None


def test_reject_non_sensitive_tool(
    db, test_user, test_conversation, approval_service
):
    with pytest.raises(ValueError):
        approval_service.create_approval(
            db=db,
            run_id="run-approval-2",
            conversation_id=test_conversation.id,
            user_id=test_user["id"],
            tool_name="get_order_status",
            arguments={"order_id": "ORD-101"},
        )


def test_reject_non_positive_expiry(
    db, test_user, test_conversation, approval_service
):
    with pytest.raises(ValueError):
        approval_service.create_approval(
            db=db,
            run_id="run-approval-3",
            conversation_id=test_conversation.id,
            user_id=test_user["id"],
            tool_name="request_refund",
            arguments={"order_id": "ORD-101"},
            expires_in_minutes=0,
        )


def test_get_approval_by_owner(
    db, test_user, test_conversation, approval_service
):
    created = approval_service.create_approval(
        db=db,
        run_id="run-approval-4",
        conversation_id=test_conversation.id,
        user_id=test_user["id"],
        tool_name="request_refund",
        arguments={"order_id": "ORD-101"},
    )

    retrieved = approval_service.get_approval(
        db=db,
        approval_id=created.approval_id,
        user_id=test_user["id"],
    )

    assert retrieved is not None
    assert retrieved.approval_id == created.approval_id


def test_prevent_cross_user_approval_access(
    db, test_user, test_conversation, approval_service
):
    created = approval_service.create_approval(
        db=db,
        run_id="run-approval-5",
        conversation_id=test_conversation.id,
        user_id=test_user["id"],
        tool_name="cancel_order",
        arguments={"order_id": "ORD-101"},
    )

    retrieved = approval_service.get_approval(
        db=db,
        approval_id=created.approval_id,
        user_id=test_user["id"] + 999999,
    )

    assert retrieved is None


@pytest.mark.parametrize("decision", ["approved", "rejected"])
def test_decide_approval(
    db, test_user, test_conversation, approval_service, decision
):
    created = approval_service.create_approval(
        db=db,
        run_id=f"run-{decision}",
        conversation_id=test_conversation.id,
        user_id=test_user["id"],
        tool_name="cancel_order",
        arguments={"order_id": "ORD-101"},
    )

    updated = approval_service.decide_approval(
        db=db,
        approval_id=created.approval_id,
        user_id=test_user["id"],
        decision=decision,
        reason="Test decision",
    )

    assert updated.status == decision
    assert updated.decision_reason == "Test decision"

    if decision == "approved":
        assert updated.approved_at is not None
    else:
        assert updated.rejected_at is not None


def test_prevent_duplicate_approval_decision(
    db, test_user, test_conversation, approval_service
):
    created = approval_service.create_approval(
        db=db,
        run_id="run-approval-duplicate",
        conversation_id=test_conversation.id,
        user_id=test_user["id"],
        tool_name="cancel_order",
        arguments={"order_id": "ORD-101"},
    )

    approval_service.decide_approval(
        db=db,
        approval_id=created.approval_id,
        user_id=test_user["id"],
        decision="approved",
    )

    with pytest.raises(ValueError):
        approval_service.decide_approval(
            db=db,
            approval_id=created.approval_id,
            user_id=test_user["id"],
            decision="rejected",
        )


def create_approved_approval(
    db, test_user, test_conversation, approval_service
):
    approval = approval_service.create_approval(
        db=db,
        run_id="run-atomic-test",
        conversation_id=test_conversation.id,
        user_id=test_user["id"],
        tool_name="cancel_order",
        arguments={"order_id": "ORD-101"},
    )

    approval_service.decide_approval(
        db=db,
        approval_id=approval.approval_id,
        user_id=test_user["id"],
        decision="approved",
    )

    return approval


def test_claim_approved_execution(
    db, test_user, test_conversation, approval_service
):
    approval = create_approved_approval(
        db, test_user, test_conversation, approval_service
    )

    claimed = approval_repository.claim_for_execution(
        db=db,
        approval_id=approval.approval_id,
        user_id=test_user["id"],
    )

    assert claimed is True

    updated = approval_service.get_approval(
        db=db,
        approval_id=approval.approval_id,
        user_id=test_user["id"],
    )

    assert updated.status == "executing"


def test_prevent_duplicate_execution_claim(
    db, test_user, test_conversation, approval_service
):
    approval = create_approved_approval(
        db, test_user, test_conversation, approval_service
    )

    first_claim = approval_repository.claim_for_execution(
        db, approval.approval_id, test_user["id"]
    )

    second_claim = approval_repository.claim_for_execution(
        db, approval.approval_id, test_user["id"]
    )

    assert first_claim is True
    assert second_claim is False


def test_cannot_claim_pending_approval(
    db, test_user, test_conversation, approval_service
):
    approval = approval_service.create_approval(
        db=db,
        run_id="run-pending-test",
        conversation_id=test_conversation.id,
        user_id=test_user["id"],
        tool_name="cancel_order",
        arguments={"order_id": "ORD-101"},
    )

    claimed = approval_repository.claim_for_execution(
        db=db,
        approval_id=approval.approval_id,
        user_id=test_user["id"],
    )

    assert claimed is False


def test_cannot_claim_another_users_approval(
    db, test_user, test_conversation, approval_service
):
    approval = create_approved_approval(
        db, test_user, test_conversation, approval_service
    )

    claimed = approval_repository.claim_for_execution(
        db=db,
        approval_id=approval.approval_id,
        user_id=test_user["id"] + 999999,
    )

    assert claimed is False

def test_complete_successful_execution(
    db, test_user, test_conversation, approval_service
):
    approval = create_approved_approval(
        db, test_user, test_conversation, approval_service
    )

    approval_repository.claim_for_execution(
        db, approval.approval_id, test_user["id"]
    )

    completed = approval_repository.complete_execution(
        db=db,
        approval_id=approval.approval_id,
        user_id=test_user["id"],
        status="executed",
        result={"success": True, "message": "Order cancelled"},
    )

    assert completed is True

    updated = approval_service.get_approval(
        db, approval.approval_id, test_user["id"]
    )

    assert updated.status == "executed"
    assert updated.executed_at is not None
    assert updated.execution_result["success"] is True


@pytest.mark.parametrize(
    "execution_status",
    ["execution_failed", "execution_unknown"],
)
def test_complete_failed_or_unknown_execution(
    db, test_user, test_conversation, approval_service, execution_status
):
    approval = create_approved_approval(
        db, test_user, test_conversation, approval_service
    )

    approval_repository.claim_for_execution(
        db, approval.approval_id, test_user["id"]
    )

    completed = approval_repository.complete_execution(
        db=db,
        approval_id=approval.approval_id,
        user_id=test_user["id"],
        status=execution_status,
        result={"success": False, "message": "Execution outcome recorded"},
    )

    assert completed is True

    updated = approval_service.get_approval(
        db, approval.approval_id, test_user["id"]
    )

    assert updated.status == execution_status
    assert updated.executed_at is None
    assert updated.execution_result["success"] is False


def test_prevent_duplicate_execution_completion(
    db, test_user, test_conversation, approval_service
):
    approval = create_approved_approval(
        db, test_user, test_conversation, approval_service
    )

    approval_repository.claim_for_execution(
        db, approval.approval_id, test_user["id"]
    )

    first_completion = approval_repository.complete_execution(
        db, approval.approval_id, test_user["id"],
        "executed", {"success": True},
    )

    second_completion = approval_repository.complete_execution(
        db, approval.approval_id, test_user["id"],
        "execution_failed", {"success": False},
    )

    assert first_completion is True
    assert second_completion is False


def test_reject_invalid_execution_status(
    db, test_user, test_conversation, approval_service
):
    approval = create_approved_approval(
        db, test_user, test_conversation, approval_service
    )

    approval_repository.claim_for_execution(
        db, approval.approval_id, test_user["id"]
    )

    with pytest.raises(ValueError, match="Invalid execution status"):
        approval_repository.complete_execution(
            db, approval.approval_id, test_user["id"],
            "pending", {},
        )
        
        
