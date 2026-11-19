from uuid import uuid4

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.api.v3.dependencies import get_current_customer_id
from app.api.v3.schemas.agent import AgentChatRequest, AgentChatResponse
from app.services.conversation_service import conversation_service
from app.services.v3.authorization import build_execution_context
from app.api.v3.dependencies import (
    get_agent_service,
    get_current_customer_id,
)


router = APIRouter(prefix="/agent", tags=["V3 Agent"])


@router.post("/chat", response_model=AgentChatResponse)
def chat(
    payload: AgentChatRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    customer_id: int = Depends(get_current_customer_id),
    agent_service = Depends(get_agent_service)
):
    if payload.conversation_id is not None:
        conversation = conversation_service.get_conversation(
            db=db,
            user_id=current_user.id,
            conversation_id=payload.conversation_id,
        )
    else:
        conversation = conversation_service.create_conversation(
            db=db,
            user_id=current_user.id,
            title=payload.message[:100],
        )

    run_id = str(uuid4())
    request_id = getattr(request.state, "request_id", str(uuid4()))

    context = build_execution_context(
        user_id=current_user.id,
        customer_id=customer_id,
        run_id=run_id,
        request_id=request_id,
        conversation_id=conversation.id,
        db=db,
    )

    result = agent_service.run(
        message=payload.message,
        context=context,
    )

    return AgentChatResponse(
        run_id=run_id,
        conversation_id=conversation.id,
        status=result.status,
        message=result.content,
        approval_id=result.approval_id,
    )
