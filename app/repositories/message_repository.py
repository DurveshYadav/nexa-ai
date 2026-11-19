from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.message import Message


class MessageRepository:

    def create(
        self,
        db: Session,
        conversation_id: int,
        role: str,
        content: str,
        model: str | None = None,
        input_tokens: int | None = None,
        output_tokens: int | None = None,
    ) -> Message:

        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )

        db.add(message)
        db.commit()
        db.refresh(message)

        return message


    def get_recent(
        self,
        db: Session,
        conversation_id: int,
        limit: int = 20,
    ) -> list[Message]:

        statement = (
            select(Message)
            .where(
                Message.conversation_id == conversation_id
            )
            .order_by(Message.created_at.desc())
            .limit(limit)
        )

        messages = list(
            db.scalars(statement).all()
        )

        messages.reverse()

        return messages

    def get_all(
        self,
        db: Session,
        conversation_id: int,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Message]:

        statement = (
            select(Message)
            .where(
                Message.conversation_id == conversation_id
            )
            .order_by(Message.created_at.asc())
            .offset(skip)
            .limit(limit)
        )

        return list(db.scalars(statement).all())
