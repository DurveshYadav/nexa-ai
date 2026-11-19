from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user
from app.api.v3.dependencies import get_agent_service
from app.api.v3.schemas.runs import (
    AgentRunHistoryResponse,
    AgentRunResponse,
)

router = APIRouter(
    prefix="/agent/runs",
    tags=["V3 Agent Runs"],
)


@router.get(
    "/{run_id}",
    response_model=AgentRunResponse,
)
def get_run(
    run_id: str,
    current_user=Depends(get_current_user),
    agent_service=Depends(get_agent_service),
):
    run_manager = agent_service.orchestrator.run_manager

    try:
        run = run_manager.get_run(
            run_id=run_id,
            user_id=current_user.id,
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent run not found.",
        )

    return run


@router.get(
    "/{run_id}/history",
    response_model=AgentRunHistoryResponse,
)
def get_run_history(
    run_id: str,
    current_user=Depends(get_current_user),
    agent_service=Depends(get_agent_service),
):
    run_manager = agent_service.orchestrator.run_manager

    try:
        steps = run_manager.get_history(
            run_id=run_id,
            user_id=current_user.id,
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent run not found.",
        )

    return AgentRunHistoryResponse(
        run_id=run_id,
        steps=steps,
    )
