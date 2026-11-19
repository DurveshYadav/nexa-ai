from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.exceptions import ResourceNotFoundError
from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.repositories.conversation_repository import ConversationRepository
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import chat_service


router = APIRouter(
    prefix="/conversations",
    tags=["Chat"],
)


conversation_repository = ConversationRepository()


@router.post(
    "/{conversation_id}/messages",
    response_model=ChatResponse,
    status_code=status.HTTP_201_CREATED,
)
def send_message(
    conversation_id: int,
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify conversation belongs to current user.
    conversation = conversation_repository.get_by_id(
        db=db,
        conversation_id=conversation_id,
        user_id=current_user.id,
    )

    # if conversation is None:
    #     from fastapi import HTTPException

    #     raise HTTPException(
    #         status_code=404,
    #         detail="Conversation not found",
    #     )

    if conversation is None:
        raise ResourceNotFoundError(
            "Conversation not found."
        )

    # Send message through service layer.
    return chat_service.send_message(
        db=db,
        conversation=conversation,
        content=request.content,
    )
    