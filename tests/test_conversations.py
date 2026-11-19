# from fastapi.testclient import TestClient

# from app.main import app


# client = TestClient(app)


# def test_create_conversation():
#     """
#     Verify successful conversation creation.
#     """

#     response = client.post(
#         "/api/v1/conversations",
#         json={
#             "title": "Python Learning",
#         },
#     )

#     assert response.status_code == 201

#     data = response.json()

#     assert data["id"] == 1
#     assert data["title"] == "Python Learning"


# def test_create_conversation_validation():
#     """
#     Verify that invalid input is rejected.
#     """

#     response = client.post(
#         "/api/v1/conversations",
#         json={
#             "title": "",
#         },
#     )

#     assert response.status_code == 422

# def test_get_conversation():
#     response = client.get(
#         "/api/v1/conversations/1"
#     )

#     assert response.status_code == 200

#     data = response.json()

#     # assert data["id"] == 1
#     assert isinstance(data["id"], int)
#     assert data["id"] > 0
#     assert data["title"] == "Python Learning"

# def test_get_conversation_not_found():
#     """
#     Verify 404 is returned when conversation does not exist.
#     """

#     response = client.get(
#         "/api/v1/conversations/999999"
#     )

#     assert response.status_code == 404

#     data = response.json()

#     assert data["detail"] == "Conversation not found"

from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def create_test_user():
    """
    Create a unique user and return JWT token.
    """

    email = f"conversation-{uuid4().hex[:8]}@example.com"
    password = "Password123"

    # Register user
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    assert register_response.status_code == 201

    # Login user
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
    """
    Create Authorization header.
    """

    return {
        "Authorization": f"Bearer {token}"
    }


def test_create_conversation():
    """
    Verify successful conversation creation.
    """

    token = create_test_user()

    response = client.post(
        "/api/v1/conversations",
        headers=auth_headers(token),
        json={
            "title": "Python Learning",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == "Python Learning"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_create_conversation_validation():
    """
    Verify invalid input is rejected.
    """

    token = create_test_user()

    response = client.post(
        "/api/v1/conversations",
        headers=auth_headers(token),
        json={
            "title": "",
        },
    )

    assert response.status_code == 422


def test_get_conversation():
    """
    Verify authenticated user can get their own conversation.
    """

    token = create_test_user()

    # Create conversation first
    create_response = client.post(
        "/api/v1/conversations",
        headers=auth_headers(token),
        json={
            "title": "Python Learning",
        },
    )

    assert create_response.status_code == 201

    conversation_id = create_response.json()["id"]

    # Get conversation
    response = client.get(
        f"/api/v1/conversations/{conversation_id}",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == conversation_id
    assert data["title"] == "Python Learning"


def test_get_conversation_not_found():
    """
    Verify 404 is returned when conversation does not exist.
    """

    token = create_test_user()

    response = client.get(
        "/api/v1/conversations/999999",
        headers=auth_headers(token),
    )

    assert response.status_code == 404

    data = response.json()
    print("\nACTUAL 404 RESPONSE:", data)
    # assert data["detail"] == "Conversation not found."
    assert data["error"]["code"] == "RESOURCE_NOT_FOUND"
    assert data["error"]["message"] == "Conversation not found"


def test_unauthenticated_conversation():
    """
    Verify conversation API requires authentication.
    """

    response = client.get(
        "/api/v1/conversations"
    )

    assert response.status_code == 401


def test_user_cannot_access_other_users_conversation():
    """
    Verify one user cannot access another user's conversation.
    """

    # User A
    token_a = create_test_user()

    create_response = client.post(
        "/api/v1/conversations",
        headers=auth_headers(token_a),
        json={
            "title": "Private Conversation",
        },
    )

    assert create_response.status_code == 201

    conversation_id = create_response.json()["id"]

    # User B
    token_b = create_test_user()

    response = client.get(
        f"/api/v1/conversations/{conversation_id}",
        headers=auth_headers(token_b),
    )

    # assert response.status_code == 404
    # assert response.json()["detail"] == "Conversation not found."
    assert response.status_code == 404
    data = response.json()
    assert data["error"]["code"] == "RESOURCE_NOT_FOUND"
    assert data["error"]["message"] == "Conversation not found"

