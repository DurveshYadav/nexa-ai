import os


TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://nexaai_user:nexaai%40123@localhost:5433/nexa_ai_test",
    ),
)

os.environ["DATABASE_URL"] = TEST_DATABASE_URL

os.environ["OPENAI_API_KEY"] = "test-key"
os.environ["OPENAI_MODEL"] = "test-model"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.database.session import get_db
from app.main import app


test_engine = create_engine(
    TEST_DATABASE_URL,
    pool_pre_ping=True,
)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autocommit=False,
    autoflush=False,
)

@pytest.fixture()
def db():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    # Create tables before tests.
    Base.metadata.create_all(bind=test_engine)

    yield

    # Remove tables after the complete test session.
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture()
def test_user(client):
    email = f"test-{uuid.uuid4().hex[:8]}@example.com"

    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "TestPassword123!",
        },
    )

    assert response.status_code in (200, 201)

    return response.json()

@pytest.fixture()
def auth_headers(client, test_user):
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user["email"],
            "password": "TestPassword123!",
        },
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }

def test_protected_endpoint(client, auth_headers):

    response = client.get(
        "/api/v1/...",
        headers=auth_headers,
    )

    assert response.status_code == 200
