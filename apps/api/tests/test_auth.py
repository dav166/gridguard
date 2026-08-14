from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.db.base import Base
from app.db.session import get_db
from app.main import create_app


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    testing_session_local = sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )

    Base.metadata.create_all(bind=engine)

    application = create_app()

    def override_get_db() -> Generator[
        Session,
        None,
        None,
    ]:
        with testing_session_local() as session:
            yield session

    application.dependency_overrides[get_db] = override_get_db

    with TestClient(application) as test_client:
        yield test_client

    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def user_payload() -> dict[str, str]:
    return {
        "email": "david@example.com",
        "full_name": "David Spaulding",
        "password": "gridguard-password-123",
    }


def test_register_creates_authenticated_user(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json=user_payload(),
    )

    assert response.status_code == 201

    body = response.json()

    assert body["email"] == "david@example.com"
    assert body["full_name"] == "David Spaulding"
    assert "password" not in body
    assert "password_hash" not in body

    cookie = response.headers["set-cookie"].lower()

    assert "gridguard_session=" in cookie
    assert "httponly" in cookie
    assert "samesite=lax" in cookie


def test_register_rejects_duplicate_email(
    client: TestClient,
) -> None:
    client.post(
        "/api/v1/auth/register",
        json=user_payload(),
    )

    response = client.post(
        "/api/v1/auth/register",
        json=user_payload(),
    )

    assert response.status_code == 409


def test_authenticated_user_can_get_me(
    client: TestClient,
) -> None:
    client.post(
        "/api/v1/auth/register",
        json=user_payload(),
    )

    response = client.get("/api/v1/auth/me")

    assert response.status_code == 200
    assert response.json()["email"] == "david@example.com"


def test_login_accepts_correct_password(
    client: TestClient,
) -> None:
    client.post(
        "/api/v1/auth/register",
        json=user_payload(),
    )

    client.post("/api/v1/auth/logout")

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "david@example.com",
            "password": "gridguard-password-123",
        },
    )

    assert response.status_code == 200
    assert response.json()["email"] == "david@example.com"


def test_login_rejects_wrong_password(
    client: TestClient,
) -> None:
    client.post(
        "/api/v1/auth/register",
        json=user_payload(),
    )

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "david@example.com",
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid email or password."}


def test_logout_revokes_session(
    client: TestClient,
) -> None:
    client.post(
        "/api/v1/auth/register",
        json=user_payload(),
    )

    logout_response = client.post("/api/v1/auth/logout")

    assert logout_response.status_code == 204

    me_response = client.get("/api/v1/auth/me")

    assert me_response.status_code == 401


def test_me_requires_authentication(
    client: TestClient,
) -> None:
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401
