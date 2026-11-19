from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    AIProviderError,
    AIProviderTimeoutError,
    DatabaseError,
    NexaAIException,
    ResourceNotFoundError,
)


async def nexai_exception_handler(
    request: Request,
    exc: NexaAIException,
):
    status_code = 500

    if isinstance(exc, ResourceNotFoundError):
        status_code = 404

    elif isinstance(exc, AIProviderTimeoutError):
        status_code = 504

    elif isinstance(exc, AIProviderError):
        status_code = 502

    elif isinstance(exc, DatabaseError):
        status_code = 500

    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
            }
        },
    )
