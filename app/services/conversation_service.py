
from sqlalchemy.orm import Session

from app.repositories.conversation_repository import (
    conversation_repository,
)
from app.core.exceptions import ResourceNotFoundError

class ConversationService:

    def create_conversation(
        self,
        db: Session,
        user_id: int,
        title: str,
    ):

        if title.lower() == "forbidden":
            raise ValueError(
                "This conversation title is not allowed."
            )

        return conversation_repository.create(
            db=db,
            user_id=user_id,
            title=title,
        )

    def get_conversation(
        self,
        db: Session,
        user_id: int,
        conversation_id: int,
    ):

        conversation = (
            conversation_repository.get_by_id(
                db=db,
                conversation_id=conversation_id,
                user_id=user_id,
            )
        )

        # if conversation is None:
        #     raise ValueError(
        #         "Conversation not found."
        #     )

        if conversation is None:
            raise ResourceNotFoundError("Conversation not found")

        return conversation

    def get_conversations(
        self,
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
    ):

        return conversation_repository.get_all(
            db=db,
            user_id=user_id,
            skip=skip,
            limit=limit,
        )

    def update_conversation(
        self,
        db: Session,
        user_id: int,
        conversation_id: int,
        title: str,
    ):

        conversation = self.get_conversation(
            db=db,
            user_id=user_id,
            conversation_id=conversation_id,
        )

        return conversation_repository.update(
            db=db,
            conversation=conversation,
            title=title,
        )

    def delete_conversation(
        self,
        db: Session,
        user_id: int,
        conversation_id: int,
    ):

        conversation = self.get_conversation(
            db=db,
            user_id=user_id,
            conversation_id=conversation_id,
        )

        conversation_repository.delete(
            db=db,
            conversation=conversation,
        )


conversation_service = ConversationService()