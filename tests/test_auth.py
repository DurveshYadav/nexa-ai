
from uuid import uuid4
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def unique_email(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8]}@example.com"

def test_register_user():
    # email = "test_register_unique@example.com"
    email = unique_email("test")

    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "Password123",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["email"] == email
    assert "password" not in data
    assert "password_hash" not in data


def test_login_user():
    # email = "test_login_unique@example.com"
    email = unique_email("login")

    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "Password123",
        },
    )

    assert register_response.status_code == 201

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": "Password123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_protected_conversation():
    # email = "test_protected_unique@example.com"
    email = unique_email("protected")

    # Register
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "Password123",
        },
    )

    assert register_response.status_code == 201

    # Login
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": "Password123",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    # Protected API
    response = client.post(
        "/api/v1/conversations",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "title": "Protected Conversation",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == "Protected Conversation"



def test_get_conversation():
    email = unique_email("get")

    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "Password123",
        },
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": "Password123",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    create_response = client.post(
        "/api/v1/conversations",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "title": "Get Test Conversation",
        },
    )

    assert create_response.status_code == 201

    conversation_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/conversations/{conversation_id}",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200
    assert response.json()["id"] == conversation_id

def test_get_nonexistent_conversation():
    email = unique_email("not-found")

    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "Password123",
        },
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": "Password123",
        },
    )

    token = login_response.json()["access_token"]

    response = client.get(
        "/api/v1/conversations/999999",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 404
    # assert response.json()["detail"] == "Conversation not found."
    data = response.json()
    assert data["error"]["code"] == "RESOURCE_NOT_FOUND"
    assert data["error"]["message"] == "Conversation not found"


