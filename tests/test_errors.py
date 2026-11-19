# from app.core.exceptions import ResourceNotFoundError


# def test_resource_not_found_exception():

#     error = ResourceNotFoundError(
#         "Conversation not found."
#     )

#     assert error.code == "RESOURCE_NOT_FOUND"
#     assert error.message == "Conversation not found."

from fastapi.testclient import TestClient

from app.core.exceptions import (
    AIProviderError,
    AIProviderTimeoutError,
    DatabaseError,
    NexaAIException,
    ResourceNotFoundError,
)
from app.main import app


client = TestClient(app)


def test_resource_not_found_exception():
    error = ResourceNotFoundError(
        "Conversation not found."
    )

    assert error.code == "RESOURCE_NOT_FOUND"
    assert error.message == "Conversation not found."


def test_resource_not_found_handler():
    @app.get("/test-error-not-found")
    def test_error_not_found():
        raise ResourceNotFoundError(
            "Test resource not found."
        )

    response = client.get(
        "/test-error-not-found"
    )

    assert response.status_code == 404

    data = response.json()

    assert data["error"]["code"] == "RESOURCE_NOT_FOUND"
    assert data["error"]["message"] == (
        "Test resource not found."
    )


def test_ai_provider_error_handler():
    @app.get("/test-error-ai")
    def test_error_ai():
        raise AIProviderError(
            "AI provider failed."
        )

    response = client.get(
        "/test-error-ai"
    )

    assert response.status_code == 502

    data = response.json()

    assert data["error"]["code"] == "AI_PROVIDER_ERROR"
    assert data["error"]["message"] == (
        "AI provider failed."
    )


def test_ai_provider_timeout_handler():
    @app.get("/test-error-ai-timeout")
    def test_error_ai_timeout():
        raise AIProviderTimeoutError(
            "AI provider timed out."
        )

    response = client.get(
        "/test-error-ai-timeout"
    )

    assert response.status_code == 504

    data = response.json()

    assert data["error"]["code"] == (
        "AI_PROVIDER_TIMEOUT"
    )
    assert data["error"]["message"] == (
        "AI provider timed out."
    )


def test_database_error_handler():
    @app.get("/test-error-database")
    def test_error_database():
        raise DatabaseError(
            "Database failed."
        )

    response = client.get(
        "/test-error-database"
    )

    assert response.status_code == 500

    data = response.json()

    assert data["error"]["code"] == "DATABASE_ERROR"
    assert data["error"]["message"] == (
        "Database failed."
    )


def test_generic_nexai_error_handler():
    @app.get("/test-error-generic")
    def test_error_generic():
        raise NexaAIException(
            "Something went wrong."
        )

    response = client.get(
        "/test-error-generic"
    )

    assert response.status_code == 500

    data = response.json()

    assert data["error"]["code"] == "NEXAAI_ERROR"
    assert data["error"]["message"] == (
        "Something went wrong."
    )
    