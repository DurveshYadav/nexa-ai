from datetime import datetime
from sqlalchemy import DateTime, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

class User(Base):
    """
    Database model for application users.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    customer_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        unique=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    agent_permissions: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=lambda: [
            "orders:read",
            "products:read",
            "customers:read",
            "support:write",
            "refunds:read",
        ],
    )

    conversations = relationship(
        "Conversation",
        back_populates="user",
    )