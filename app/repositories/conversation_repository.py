
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.conversation import Conversation


class ConversationRepository:

    def create(
        self,
        db: Session,
        user_id: int,
        title: str,
    ) -> Conversation:

        conversation = Conversation(
            user_id=user_id,
            title=title,
        )

        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        return conversation

    def get_by_id(
        self,
        db: Session,
        conversation_id: int,
        user_id: int,
    ) -> Conversation | None:

        statement = (
            select(Conversation)
            .where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,
            )
        )

        return db.execute(
            statement
        ).scalar_one_or_none()

    def get_by_id_for_user(
        self,
        db: Session,
        conversation_id: int,
        user_id: int,
    ) -> Conversation | None:

        statement = (
            select(Conversation)
            .where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,
            )
        )

        return db.scalars(statement).first()


    def get_all(
        self,
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Conversation]:

        statement = (
            select(Conversation)
            .where(
                Conversation.user_id == user_id
            )
            .order_by(
                Conversation.created_at.desc()
            )
            .offset(skip)
            .limit(limit)
        )

        return list(
            db.execute(
                statement
            ).scalars().all()
        )

    def update(
        self,
        db: Session,
        conversation: Conversation,
        title: str,
    ) -> Conversation:

        conversation.title = title

        db.commit()
        db.refresh(conversation)

        return conversation

    def delete(
        self,
        db: Session,
        conversation: Conversation,
    ) -> None:

        db.delete(conversation)
        db.commit()


conversation_repository = ConversationRepository()