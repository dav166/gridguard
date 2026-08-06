from fastapi.testclient import TestClient

from app.main import create_app

client = TestClient(create_app())


def test_health_check_returns_service_status() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "GridGuard API",
        "environment": "development",
        "version": "0.1.0",
    }


def test_openapi_schema_is_available() -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert response.json()["info"]["title"] == "GridGuard API"