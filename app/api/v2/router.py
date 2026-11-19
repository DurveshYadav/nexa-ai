from fastapi import APIRouter

from app.api.v2.endpoints import ml


api_v2_router = APIRouter(
    prefix="/api/v2",
)

api_v2_router.include_router(ml.router)
