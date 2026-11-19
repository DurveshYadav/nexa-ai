from fastapi import APIRouter


# Router responsible for health-related endpoints.
router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get("")
def health_check():
    """
    Check whether the NexaAI API is running.
    """

    return {
        "status": "healthy"
    }