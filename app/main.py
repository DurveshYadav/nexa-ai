
import logging
import time
import uuid
from fastapi import FastAPI, Request
from app.core.exception_handlers import nexai_exception_handler
from app.core.exceptions import NexaAIException
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging
from fastapi.middleware.cors import CORSMiddleware
from app.api.v2.router import api_v2_router
from app.core.observability import configure_logging
from app.middleware.request_context import RequestContextMiddleware


logger = logging.getLogger(__name__)
setup_logging()
configure_logging()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="NexaAI V1 - AI Assistant REST API",
    debug=settings.debug,
)

app.add_exception_handler(
    NexaAIException,
    nexai_exception_handler,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RequestContextMiddleware)
# @app.middleware("http")
# async def log_request_time(
#     request: Request,
#     call_next,
# ):
#     """
#     Measure how long each HTTP request takes.
#     """

#     start_time = time.perf_counter()

#     # Continue to the actual endpoint.
#     response = await call_next(request)

#     # Calculate execution time.
#     duration = time.perf_counter() - start_time

#     print(
#         f"{request.method} "
#         f"{request.url.path} "
#         f"{response.status_code} "
#         f"{duration:.4f}s"
#     )

#     return response

@app.middleware("http")
async def log_request_time(
    request: Request,
    call_next,
):
    """
    Add request ID and log request timing.
    """

    # Generate a unique ID for this request.
    request_id = str(uuid.uuid4())

    # Store it on the request so other layers can access it.
    request.state.request_id = request_id

    # Start request timer.
    start_time = time.perf_counter()

    logger.info(
        "request_started "
        "request_id=%s method=%s path=%s",
        request_id,
        request.method,
        request.url.path,
    )

    try:
        # Continue to the actual endpoint.
        response = await call_next(request)

        # Calculate request duration.
        duration_ms = (
            time.perf_counter() - start_time
        ) * 1000

        # Return request ID to the client.
        response.headers["X-Request-ID"] = request_id

        logger.info(
            "request_completed "
            "request_id=%s status=%s duration_ms=%.2f",
            request_id,
            response.status_code,
            duration_ms,
        )

        return response

    except Exception:
        # Calculate duration even when request fails.
        duration_ms = (
            time.perf_counter() - start_time
        ) * 1000

        # logger.exception() automatically includes traceback.
        logger.exception(
            "request_failed "
            "request_id=%s method=%s path=%s duration_ms=%.2f",
            request_id,
            request.method,
            request.url.path,
            duration_ms,
        )

        # Let Phase 9 exception handling continue working.
        raise

# Register API routes.
app.include_router(api_router)
app.include_router(api_v2_router)

@app.get("/", tags=["Root"])
def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "message": "NexaAI API is running",
    }


