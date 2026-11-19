
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.api.v3.dependencies import (
    get_agent_service,
    get_current_customer_id,
)
from app.api.v3.schemas.approvals import (
    ApprovalDecision,
    ApprovalResponse,
)
from app.models.conversation import Conversation
from app.services.v3.approval_service import (
    SENSITIVE_TOOLS,
    approval_service,
)
from app.services.v3.authorization import build_execution_context


router = APIRouter(
    prefix="/agent/approvals",
    tags=["V3 Agent Approvals"],
)


def build_approval_response(approval) -> ApprovalResponse:
    return ApprovalResponse(
        approval_id=approval.approval_id,
        run_id=approval.run_id,
        conversation_id=approval.conversation_id,
        tool_name=approval.tool_name,
        status=approval.status,
        created_at=approval.created_at,
        expires_at=approval.expires_at,
        approved_at=approval.approved_at,
        rejected_at=approval.rejected_at,
        executed_at=approval.executed_at,
        decision_reason=approval.decision_reason,
        execution_result=approval.execution_result,
    )


@router.get(
    "/{approval_id}",
    response_model=ApprovalResponse,
)
def get_approval(
    approval_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    approval = approval_service.get_approval(
        db=db,
        approval_id=approval_id,
        user_id=current_user.id,
    )

    if approval is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval not found",
        )

    return build_approval_response(approval)


@router.post(
    "/{approval_id}/confirm",
    response_model=ApprovalResponse,
)
def confirm_approval(
    approval_id: str,
    payload: ApprovalDecision,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if payload.approval_id != approval_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Approval ID in path and body do not match",
        )

    approval = approval_service.get_approval(
        db=db,
        approval_id=approval_id,
        user_id=current_user.id,
    )

    if approval is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval not found",
        )

    try:
        approval = approval_service.decide_approval(
            db=db,
            approval_id=approval_id,
            user_id=current_user.id,
            decision=payload.decision,
            reason=payload.reason,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return build_approval_response(approval)


@router.post(
    "/{approval_id}/execute",
    response_model=ApprovalResponse,
)
def execute_approval(
    approval_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    customer_id: int = Depends(get_current_customer_id),
    agent_service=Depends(get_agent_service),
):
    # 1. Retrieve approval belonging to authenticated user.
    approval = approval_service.get_approval(
        db=db,
        approval_id=approval_id,
        user_id=current_user.id,
    )

    if approval is None:
        raise HTTPException(
            status_code=404,
            detail="Approval not found",
        )

    # 2. Verify conversation ownership.
    conversation = db.get(
        Conversation,
        approval.conversation_id,
    )

    if conversation is None or conversation.user_id != current_user.id:
        raise HTTPException(
            status_code=404,
            detail="Approval not found",
        )

    # 3. Only explicitly approved actions can execute.
    if approval.status != "approved":
        raise HTTPException(
            status_code=409,
            detail=f"Approval cannot execute from status: {approval.status}",
        )

    if approval.tool_name not in SENSITIVE_TOOLS:
        raise HTTPException(
            status_code=409,
            detail="Tool is not eligible for approval execution",
        )

    # 4. Validate registered tool and stored arguments.
    try:
        tool = agent_service.registry.get(approval.tool_name)
    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail="Approved tool is unavailable",
        ) from exc

    if not tool.enabled:
        raise HTTPException(
            status_code=409,
            detail="Approved tool is disabled",
        )

    try:
        validated_arguments = tool.input_schema.model_validate(
            approval.arguments
        )
    except ValidationError as exc:
        raise HTTPException(
            status_code=409,
            detail="Stored approval arguments are invalid",
        ) from exc

    # 5. Build a fresh trusted authorization context.
    try:
        context = build_execution_context(
            user_id=current_user.id,
            customer_id=customer_id,
            run_id=approval.run_id,
            request_id=getattr(
                request.state,
                "request_id",
                approval.idempotency_key,
            ),
            conversation_id=approval.conversation_id,
            db=db,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=403,
            detail="User authorization context is invalid",
        ) from exc

    # Recheck current permissions before claiming execution.
    if tool.permission and tool.permission not in context.permissions:
        raise HTTPException(
            status_code=403,
            detail="You no longer have permission to execute this action",
        )

    # 6. Atomically claim the approval.
    claimed = approval_service.repository.claim_for_execution(
        db=db,
        approval_id=approval_id,
        user_id=current_user.id,
    )

    if not claimed:
        raise HTTPException(
            status_code=409,
            detail="Approval expired or execution was already claimed",
        )

    # 7. Execute exactly once. An uncertain outcome must never be retried.
    try:
        tool_result = agent_service.executor.execute(
            tool_name=approval.tool_name,
            arguments=validated_arguments.model_dump(mode="json"),
            context=context,
        )

        execution_result = tool_result.model_dump(mode="json")

        if tool_result.success:
            final_status = "executed"
        elif (
            tool_result.error
            and tool_result.error.code == "EXECUTION_ERROR"
        ):
            final_status = "execution_unknown"
        else:
            final_status = "execution_failed"

    except Exception:
        final_status = "execution_unknown"
        execution_result = {
            "success": False,
            "error": {
                "code": "EXECUTION_ERROR",
                "message": "Execution outcome could not be confirmed.",
            },
        }

    # 8. Persist the final execution state.
    completed = approval_service.repository.complete_execution(
        db=db,
        approval_id=approval_id,
        user_id=current_user.id,
        status=final_status,
        result=execution_result,
    )

    if not completed:
        raise HTTPException(
            status_code=500,
            detail=(
                "Execution outcome could not be persisted. "
                "Do not retry this action; it requires reconciliation."
            ),
        )

    db.refresh(approval)

    return build_approval_response(approval)

