from fastapi import APIRouter

from app.api.v1.endpoints import (
    chat,
    ai,
    auth,
    health,
    conversations,
)

# Main router for API version 1.
api_router = APIRouter(
    prefix="/api/v1",
)


# Health endpoints.
api_router.include_router(
    health.router,
)

api_router.include_router(auth.router)

# Conversation endpoints.
api_router.include_router(
    conversations.router,
)

api_router.include_router(ai.router)
api_router.include_router(chat.router)

