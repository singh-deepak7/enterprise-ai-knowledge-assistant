from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200

    body = response.json()

    assert "status" in body
    assert "application" in body
    assert "version" in body
    assert "services" in body
    assert "timestamp" in body


def test_ready() -> None:
    response = client.get("/api/v1/ready")

    assert response.status_code == 200

    body = response.json()

    assert "ready" in body
    assert "status" in body


def test_version() -> None:
    response = client.get("/api/v1/version")

    assert response.status_code == 200

    body = response.json()

    assert "application" in body
    assert "version" in body
    assert "model" in body