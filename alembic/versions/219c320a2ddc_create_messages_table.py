"""create messages table

Revision ID: 219c320a2ddc
Revises: 7b1b0ec4a75a
Create Date: 2026-09-25 17:33:15.074257

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# Alembic revision identifiers.
revision: str = "219c320a2ddc"
down_revision: Union[str, Sequence[str], None] = "7b1b0ec4a75a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create messages table."""

    op.create_table(
        "messages",

        # Primary key.
        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            nullable=False,
        ),

        # Conversation reference.
        sa.Column(
            "conversation_id",
            sa.Integer(),
            sa.ForeignKey("conversations.id"),
            nullable=False,
        ),

        # user / assistant / system.
        sa.Column(
            "role",
            sa.String(),
            nullable=False,
        ),

        # Message text.
        sa.Column(
            "content",
            sa.Text(),
            nullable=False,
        ),

        # LLM model used for assistant response.
        sa.Column(
            "model",
            sa.String(),
            nullable=True,
        ),

        # Token usage.
        sa.Column(
            "input_tokens",
            sa.Integer(),
            nullable=True,
        ),

        sa.Column(
            "output_tokens",
            sa.Integer(),
            nullable=True,
        ),

        # Message creation time.
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
        ),
    )

    # Index for faster conversation message queries.
    op.create_index(
        "ix_messages_conversation_id",
        "messages",
        ["conversation_id"],
    )


def downgrade() -> None:
    """Drop messages table."""

    op.drop_index(
        "ix_messages_conversation_id",
        table_name="messages",
    )

    op.drop_table("messages")
    
    
    