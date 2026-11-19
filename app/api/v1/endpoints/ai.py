from fastapi import APIRouter, Depends

from app.ai.schemas import AIMessage
from app.ai.service import ai_service
from app.api.deps import get_current_user
from app.models.user import User
from app.ai.prompts import DEFAULT_SYSTEM_PROMPT


router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


@router.post("/test")
def test_ai(
    current_user: User = Depends(get_current_user),
):
    """
    Development endpoint for testing LLM integration.
    """

    response = ai_service.generate_response(
        [
            AIMessage(
                role="system",
                # content="You are NexaAI, a helpful assistant.",
                content=DEFAULT_SYSTEM_PROMPT,
            ),
            AIMessage(
                role="user",
                content="Say hello in one sentence.",
            ),
        ]
    )

    return response
