
"""extend agent approval execution statuses

Revision ID: bc8f9ad08dbc
Revises: a1fe50a793be
"""

from typing import Sequence, Union

from alembic import op

revision: str = "bc8f9ad08dbc"
down_revision: Union[str, Sequence[str], None] = "a1fe50a793be"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(
        "ck_agent_approvals_status",
        "agent_approvals",
        type_="check",
    )

    op.create_check_constraint(
        "ck_agent_approvals_status",
        "agent_approvals",
        """
        status IN (
            'pending',
            'approved',
            'rejected',
            'expired',
            'cancelled',
            'executing',
            'executed',
            'execution_failed',
            'execution_unknown'
        )
        """,
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_agent_approvals_status",
        "agent_approvals",
        type_="check",
    )

    op.create_check_constraint(
        "ck_agent_approvals_status",
        "agent_approvals",
        """
        status IN (
            'pending',
            'approved',
            'rejected',
            'expired',
            'cancelled'
        )
        """,
    )
