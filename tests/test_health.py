from fastapi.testclient import TestClient

from app.main import app


# Test client allows us to call FastAPI without
# starting a real Uvicorn server.
client = TestClient(app)


def test_health_check():
    """
    Verify that the health endpoint works.
    """

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy"
    }