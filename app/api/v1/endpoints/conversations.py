
# from fastapi import APIRouter, Depends, Query,HTTPException, status
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.conversation import (
    ConversationCreate,
    ConversationResponse,
    ConversationUpdate,
)
from app.services.conversation_service import (
    conversation_service,
)

from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository
from app.schemas.chat import MessageHistoryResponse
conversation_repository = ConversationRepository()
message_repository = MessageRepository()


router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
)

@router.post(
    "",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_conversation(
    data: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create conversation for current user.
    """

    return conversation_service.create_conversation(
        db=db,
        user_id=current_user.id,
        title=data.title,
    )

@router.get(
    "",
    response_model=list[ConversationResponse],
)
def get_conversations(
    skip: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get conversations belonging to current user.
    """

    return conversation_service.get_conversations(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
    )

@router.get(
    "/{conversation_id}",
    response_model=ConversationResponse,
)
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get one conversation owned by current user.
    """

    return conversation_service.get_conversation(
        db=db,
        conversation_id=conversation_id,
        user_id=current_user.id,
    )

@router.patch(
    "/{conversation_id}",
    response_model=ConversationResponse,
)
def update_conversation(
    conversation_id: int,
    data: ConversationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update a conversation.
    """

    return conversation_service.update_conversation(
        db=db,
        user_id=current_user.id,
        conversation_id=conversation_id,
        title=data.title,
    )

@router.delete(
    "/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete conversation owned by current user.
    """

    conversation_service.delete_conversation(
        db=db,
        user_id=current_user.id,
        conversation_id=conversation_id,
    )


@router.get(
    "/{conversation_id}/messages",
    response_model=MessageHistoryResponse,
)
def get_conversation_messages(
    conversation_id: int,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify ownership.
    # conversation = ConversationRepository.get_by_id_for_user(
    #     db=db,
    #     conversation_id=conversation_id,
    #     user_id=current_user.id,
    # )

    conversation = conversation_repository.get_by_id_for_user(
        db=db,
        conversation_id=conversation_id,
        user_id=current_user.id,
    )

    # if conversation is None:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         detail="Conversation not found",
    #     )
    if conversation is None:
        raise ResourceNotFoundError("Conversation not found")

    # Get messages.
    # messages = MessageRepository.get_all(
    #     db=db,
    #     conversation_id=conversation_id,
    #     skip=skip,
    #     limit=limit,
    # )

    messages = message_repository.get_all(
        db=db,
        conversation_id=conversation_id,
        skip=skip,
        limit=limit,
    )

    return MessageHistoryResponse(
        items=messages,
        skip=skip,
        limit=limit,
    )
