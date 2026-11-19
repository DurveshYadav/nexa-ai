
from sqlalchemy.orm import Session

from app.models.user import User
from app.tools.v3.context import ExecutionContext


KNOWN_AGENT_PERMISSIONS = frozenset({
    "orders:read",
    "orders:write",
    "products:read",
    "customers:read",
    "support:write",
    "refunds:read",
    "refunds:write",
})


def build_execution_context(
    user_id: int,
    customer_id: int,
    run_id: str,
    request_id: str,
    conversation_id: int | None = None,
    db: Session | None = None,
) -> ExecutionContext:
    if db is None:
        raise ValueError("Database session is required for authorization.")

    user = db.get(User, user_id)

    if user is None:
        raise ValueError("Authenticated user not found.")

    if user.customer_id is None or user.customer_id != customer_id:
        raise ValueError("User customer mapping is invalid.")

    stored_permissions = user.agent_permissions or []

    permissions = frozenset(
        permission
        for permission in stored_permissions
        if permission in KNOWN_AGENT_PERMISSIONS
    )

    return ExecutionContext(
        user_id=user.id,
        customer_id=user.customer_id,
        run_id=run_id,
        request_id=request_id,
        permissions=permissions,
        conversation_id=conversation_id,
        db=db,
    )
