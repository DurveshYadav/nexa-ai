from fastapi import APIRouter

from app.api.v3.endpoints import agent, approvals, runs


api_v3_router = APIRouter(prefix="/api/v3")

api_v3_router.include_router(agent.router)
api_v3_router.include_router(approvals.router)
api_v3_router.include_router(runs.router)
