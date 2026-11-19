"""add users and conversation ownership

Revision ID: 7b1b0ec4a75a
Revises: a7d100f111fe
Create Date: 2026-09-24 16:47:40.151197

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7b1b0ec4a75a"
down_revision: Union[str, Sequence[str], None] = "a7d100f111fe"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # 1. Create users table.
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # 2. Create user indexes.
    op.create_index(
        op.f("ix_users_email"),
        "users",
        ["email"],
        unique=True,
    )

    op.create_index(
        op.f("ix_users_id"),
        "users",
        ["id"],
        unique=False,
    )

    # 3. Create a temporary legacy user for existing conversations.
    op.execute(
        """
        INSERT INTO users
            (email, password_hash, created_at, updated_at)
        VALUES
            (
                'legacy@nexa-ai.local',
                'LEGACY_MIGRATION_USER',
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP
            )
        """
    )

    # 4. Add user_id temporarily as nullable.
    op.add_column(
        "conversations",
        sa.Column("user_id", sa.Integer(), nullable=True),
    )

    # 5. Assign existing conversations to the legacy user.
    op.execute(
        """
        UPDATE conversations
        SET user_id = (
            SELECT id
            FROM users
            WHERE email = 'legacy@nexa-ai.local'
        )
        WHERE user_id IS NULL
        """
    )

    # 6. Make user_id mandatory.
    op.alter_column(
        "conversations",
        "user_id",
        existing_type=sa.Integer(),
        nullable=False,
    )

    # 7. Create index.
    op.create_index(
        op.f("ix_conversations_user_id"),
        "conversations",
        ["user_id"],
        unique=False,
    )

    # 8. Add foreign key.
    op.create_foreign_key(
        "fk_conversations_user_id_users",
        "conversations",
        "users",
        ["user_id"],
        ["id"],
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(
        "fk_conversations_user_id_users",
        "conversations",
        type_="foreignkey",
    )

    op.drop_index(
        op.f("ix_conversations_user_id"),
        table_name="conversations",
    )

    op.drop_column(
        "conversations",
        "user_id",
    )

    op.drop_index(
        op.f("ix_users_id"),
        table_name="users",
    )

    op.drop_index(
        op.f("ix_users_email"),
        table_name="users",
    )

    op.drop_table("users")