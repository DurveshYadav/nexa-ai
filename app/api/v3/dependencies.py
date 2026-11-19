
from functools import lru_cache

from fastapi import Depends, HTTPException, status

from app.api.deps import get_current_user
from app.services.v3.agent_service import AgentService


@lru_cache(maxsize=1)
def get_agent_service() -> AgentService:
    return AgentService()


def get_current_customer_id(
    current_user=Depends(get_current_user),
) -> int:
    """
    Resolve the authenticated user's customer ID.

    Customer IDs must come from the database mapping,
    never from client or LLM input.
    """
    if current_user.customer_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No customer account is linked to this user.",
        )

    return current_user.customer_id
