
"""add agent permissions to users

Revision ID: a1fe50a793be
Revises: 83f48e48706d
Create Date: 2026-11-17 15:26:28.367953
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a1fe50a793be"
down_revision: Union[str, Sequence[str], None] = "83f48e48706d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


DEFAULT_PERMISSIONS = [
    "orders:read",
    "products:read",
    "customers:read",
    "support:write",
    "refunds:read",
]


def upgrade() -> None:
    # Add the column as nullable first so existing users can be backfilled.
    op.add_column(
        "users",
        sa.Column("agent_permissions", sa.JSON(), nullable=True),
    )

    # Give existing users the safe default permissions.
    users_table = sa.table(
        "users",
        sa.column("agent_permissions", sa.JSON()),
    )

    op.execute(
        users_table.update().values(
            agent_permissions=DEFAULT_PERMISSIONS
        )
    )

    # Enforce NOT NULL after backfilling.
    op.alter_column(
        "users",
        "agent_permissions",
        existing_type=sa.JSON(),
        nullable=False,
    )


def downgrade() -> None:
    op.drop_column("users", "agent_permissions")
