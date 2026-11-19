"""add customer mapping to users

Revision ID: 6861215ddcae
Revises: 219c320a2ddc
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "6861215ddcae"
down_revision: Union[str, Sequence[str], None] = "219c320a2ddc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("customer_id", sa.Integer(), nullable=True),
    )

    op.create_index(
        op.f("ix_users_customer_id"),
        "users",
        ["customer_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_users_customer_id"),
        table_name="users",
    )

    op.drop_column("users", "customer_id")
    