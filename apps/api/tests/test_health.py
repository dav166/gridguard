from collections.abc import Generator
from unittest.mock import Mock

from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.main import create_app


def create_client(*, database_available: bool = True) -> TestClient:
    application = create_app()
    database_session = Mock(spec=Session)

    if not database_available:
        database_session.execute.side_effect = SQLAlchemyError(
            "Database unavailable"
        )

    def override_get_db() -> Generator[Session, None, None]:
        yield database_session

    application.dependency_overrides[get_db] = override_get_db

    return TestClient(application)


def test_health_check_returns_connected_database_status() -> None:
    client = create_client()

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "GridGuard API",
        "environment": "development",
        "version": "0.1.0",
        "database": "connected",
    }


def test_health_check_returns_degraded_status_when_database_fails() -> None:
    client = create_client(database_available=False)

    response = client.get("/api/v1/health")

    assert response.status_code == 503
    assert response.json() == {
        "status": "degraded",
        "service": "GridGuard API",
        "environment": "development",
        "version": "0.1.0",
        "database": "unavailable",
    }


def test_openapi_schema_is_available() -> None:
    client = create_client()

    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert response.json()["info"]["title"] == "GridGuard API"