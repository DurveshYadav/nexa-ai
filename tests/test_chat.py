from unittest.mock import patch
from uuid import uuid4

from fastapi.testclient import TestClient

from app.ai.schemas import AIResponse
from app.main import app


client = TestClient(app)


def create_test_user():
    """
    Create a unique user and return JWT token.
    """

    email = f"chat-{uuid4().hex[:8]}@example.com"
    password = "Password123"

    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    return login_response.json()["access_token"]


def auth_headers(token: str):
    return {
        "Authorization": f"Bearer {token}"
    }


def create_test_conversation(token: str):
    """
    Create a conversation and return its ID.
    """

    response = client.post(
        "/api/v1/conversations",
        headers=auth_headers(token),
        json={
            "title": "Chat Test",
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


@patch(
    "app.services.chat_service.ai_service.generate_response"
)
def test_send_message_success(mock_generate_response):
    """
    Verify successful chat request.

    The real LLM is NOT called.
    """

    # Arrange
    token = create_test_user()
    conversation_id = create_test_conversation(token)

    mock_generate_response.return_value = AIResponse(
        content="FastAPI is a Python web framework.",
        model="test-model",
        input_tokens=10,
        output_tokens=8,
    )

    # Act
    response = client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        headers=auth_headers(token),
        json={
            "content": "What is FastAPI?",
        },
    )

    # Assert HTTP response
    assert response.status_code == 201

    data = response.json()

    # User message
    assert data["user_message"]["role"] == "user"
    assert data["user_message"]["content"] == "What is FastAPI?"

    # Assistant message
    assert data["assistant_message"]["role"] == "assistant"
    assert (
        data["assistant_message"]["content"]
        == "FastAPI is a Python web framework."
    )

    # AI metadata
    assert data["model"] == "test-model"
    assert data["input_tokens"] == 10
    assert data["output_tokens"] == 8

    # AI must be called exactly once
    mock_generate_response.assert_called_once()


@patch(
    "app.services.chat_service.ai_service.generate_response"
)
def test_send_message_uses_current_message(mock_generate_response):
    """
    Verify the current user message is included in LLM context.
    """

    token = create_test_user()
    conversation_id = create_test_conversation(token)

    mock_generate_response.return_value = AIResponse(
        content="Test response",
        model="test-model",
        input_tokens=5,
        output_tokens=3,
    )

    response = client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        headers=auth_headers(token),
        json={
            "content": "Hello NexaAI",
        },
    )

    assert response.status_code == 201

    mock_generate_response.assert_called_once()

    ai_messages = mock_generate_response.call_args.args[0]

    assert ai_messages[-1].role == "user"
    assert ai_messages[-1].content == "Hello NexaAI"


def test_send_message_nonexistent_conversation():
    """
    Verify chat returns the Phase 9 error contract
    when the conversation does not exist.
    """

    token = create_test_user()

    response = client.post(
        "/api/v1/conversations/999999/messages",
        headers=auth_headers(token),
        json={
            "content": "Hello",
        },
    )

    assert response.status_code == 404

    data = response.json()

    assert data["error"]["code"] == "RESOURCE_NOT_FOUND"
    assert data["error"]["message"] == "Conversation not found."


def test_user_cannot_send_message_to_other_users_conversation():
    """
    Verify conversation ownership is enforced for chat.
    """

    # User A creates conversation
    token_a = create_test_user()

    conversation_id = create_test_conversation(token_a)

    # User B attempts to send a message
    token_b = create_test_user()

    response = client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        headers=auth_headers(token_b),
        json={
            "content": "This should not be allowed.",
        },
    )

    assert response.status_code == 404

    data = response.json()

    assert data["error"]["code"] == "RESOURCE_NOT_FOUND"
    assert data["error"]["message"] == "Conversation not found."


def test_send_message_requires_authentication():
    """
    Verify chat endpoint requires authentication.
    """

    response = client.post(
        "/api/v1/conversations/999999/messages",
        json={
            "content": "Hello",
        },
    )

    assert response.status_code == 401
    