
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.approval import AgentApproval
from sqlalchemy import select, update

class ApprovalRepository:

    def create(
        self,
        db: Session,
        approval_id: str,
        run_id: str,
        conversation_id: int,
        user_id: int,
        tool_name: str,
        arguments: dict,
        idempotency_key: str,
        expires_at: datetime,
    ) -> AgentApproval:

        approval = AgentApproval(
            approval_id=approval_id,
            run_id=run_id,
            conversation_id=conversation_id,
            user_id=user_id,
            tool_name=tool_name,
            arguments=arguments,
            idempotency_key=idempotency_key,
            expires_at=expires_at,
            status="pending",
        )

        db.add(approval)
        db.commit()
        db.refresh(approval)

        return approval

    def get_by_approval_id(
        self,
        db: Session,
        approval_id: str,
        user_id: int,
    ) -> AgentApproval | None:

        statement = select(AgentApproval).where(
            AgentApproval.approval_id == approval_id,
            AgentApproval.user_id == user_id,
        )

        return db.scalars(statement).first()

    def get_pending(
        self,
        db: Session,
        approval_id: str,
        user_id: int,
    ) -> AgentApproval | None:

        statement = select(AgentApproval).where(
            AgentApproval.approval_id == approval_id,
            AgentApproval.user_id == user_id,
            AgentApproval.status == "pending",
        )

        return db.scalars(statement).first()

    def update_decision(
        self,
        db: Session,
        approval: AgentApproval,
        decision: str,
        reason: str | None = None,
    ) -> AgentApproval:

        now = datetime.now(timezone.utc)

        approval.status = decision
        approval.decision_reason = reason

        if decision == "approved":
            approval.approved_at = now
        elif decision == "rejected":
            approval.rejected_at = now

        db.commit()
        db.refresh(approval)

        return approval

    def mark_executed(
        self,
        db: Session,
        approval: AgentApproval,
        result: dict,
    ) -> AgentApproval:

        approval.executed_at = datetime.now(timezone.utc)
        approval.execution_result = result

        db.commit()
        db.refresh(approval)

        return approval


    def decide_pending(
        self,
        db: Session,
        approval_id: str,
        user_id: int,
        decision: str,
        reason: str | None = None,
    ) -> bool:

        now = datetime.now(timezone.utc)

        values = {
            "status": decision,
            "decision_reason": reason,
        }

        if decision == "approved":
            values["approved_at"] = now
        elif decision == "rejected":
            values["rejected_at"] = now

        statement = (
            update(AgentApproval)
            .where(
                AgentApproval.approval_id == approval_id,
                AgentApproval.user_id == user_id,
                AgentApproval.status == "pending",
                AgentApproval.expires_at > now,
            )
            .values(**values)
        )

        result = db.execute(statement)
        db.commit()

        return result.rowcount == 1
    
    
    def claim_for_execution(
        self,
        db: Session,
        approval_id: str,
        user_id: int,
    ) -> bool:
        statement = (
            update(AgentApproval)
            .where(
                AgentApproval.approval_id == approval_id,
                AgentApproval.user_id == user_id,
                AgentApproval.status == "approved",
                AgentApproval.expires_at > datetime.now(timezone.utc),
            )
            .values(status="executing")
        )

        result = db.execute(statement)
        db.commit()

        return result.rowcount == 1

    
    
    def complete_execution(
        self,
        db: Session,
        approval_id: str,
        user_id: int,
        status: str,
        result: dict,
    ) -> bool:
        if status not in {
            "executed",
            "execution_failed",
            "execution_unknown",
        }:
            raise ValueError("Invalid execution status")

        values = {
            "status": status,
            "execution_result": result,
        }

        if status == "executed":
            values["executed_at"] = datetime.now(timezone.utc)

        statement = (
            update(AgentApproval)
            .where(
                AgentApproval.approval_id == approval_id,
                AgentApproval.user_id == user_id,
                AgentApproval.status == "executing",
            )
            .values(**values)
        )

        update_result = db.execute(statement)
        db.commit()

        return update_result.rowcount == 1




approval_repository = ApprovalRepository()
