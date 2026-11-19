
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.approval import AgentApproval
from app.repositories.approval_repository import approval_repository
import logging as std_logging

logger = std_logging.getLogger(__name__)

SENSITIVE_TOOLS = frozenset({
    "cancel_order",
    "request_refund",
})


class ApprovalService:

    def __init__(self, repository=approval_repository):
        self.repository = repository

    def create_approval(
        self,
        db: Session,
        run_id: str,
        conversation_id: int,
        user_id: int,
        tool_name: str,
        arguments: dict,
        expires_in_minutes: int = 15,
    ) -> AgentApproval:

        if tool_name not in SENSITIVE_TOOLS:
            raise ValueError("Tool does not require approval")

        if expires_in_minutes <= 0:
            raise ValueError("Approval expiry must be positive")

        now = datetime.now(timezone.utc)

        approval = self.repository.create(
            db=db,
            approval_id=str(uuid4()),
            run_id=run_id,
            conversation_id=conversation_id,
            user_id=user_id,
            tool_name=tool_name,
            arguments=arguments,
            idempotency_key=str(uuid4()),
            expires_at=now + timedelta(minutes=expires_in_minutes),
        )

        logger.info(
            "approval_created approval_id=%s run_id=%s tool_name=%s",
            approval.approval_id,
            run_id,
            tool_name,
        )

        return approval

    def get_approval(
        self,
        db: Session,
        approval_id: str,
        user_id: int,
    ) -> AgentApproval | None:

        approval = self.repository.get_by_approval_id(
            db,
            approval_id,
            user_id,
        )

        if approval is None:
            return None

        if (
            approval.status in {"pending", "approved"}
            and approval.expires_at <= datetime.now(timezone.utc)
        ):
            approval.status = "expired"
            db.commit()
            db.refresh(approval)

        logger.info(
            "approval_expired approval_id=%s run_id=%s tool_name=%s",
            approval.approval_id,
            approval.run_id,
            approval.tool_name,
        )

        return approval

    def decide_approval(
        self,
        db: Session,
        approval_id: str,
        user_id: int,
        decision: str,
        reason: str | None = None,
    ) -> AgentApproval:

        if decision not in {"approved", "rejected"}:
            raise ValueError("Invalid approval decision")

        approval = self.get_approval(
            db,
            approval_id,
            user_id,
        )

        if approval is None:
            raise ValueError("Approval not found")

        if approval.status != "pending":
            raise ValueError(
                f"Approval is already {approval.status}"
            )

        updated = self.repository.decide_pending(
            db=db,
            approval_id=approval_id,
            user_id=user_id,
            decision=decision,
            reason=reason,
        )

        if not updated:
            raise ValueError(
                "Approval expired or was already processed"
            )

        result = self.repository.get_by_approval_id(
            db,
            approval_id,
            user_id,
        )

        logger.info(
            "approval_decided approval_id=%s run_id=%s "
            "tool_name=%s decision=%s",
            result.approval_id,
            result.run_id,
            result.tool_name,
            decision,
        )

        return result


approval_service = ApprovalService()
