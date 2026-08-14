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

PASSWORD = "gridguard-password-123"


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={
            "check_same_thread": False,
        },
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


def register_user(
    client: TestClient,
    email: str,
) -> dict[str, object]:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "full_name": "GridGuard User",
            "password": PASSWORD,
        },
    )

    assert response.status_code == 201

    return response.json()


def login_user(
    client: TestClient,
    email: str,
) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": PASSWORD,
        },
    )

    assert response.status_code == 200


def create_organization(
    client: TestClient,
) -> dict[str, object]:
    response = client.post(
        "/api/v1/organizations",
        json={
            "name": "Northstar Renewables",
            "slug": "northstar-renewables",
        },
    )

    assert response.status_code == 201

    return response.json()


def test_organization_creator_becomes_admin(
    client: TestClient,
) -> None:
    admin = register_user(
        client,
        "admin@example.com",
    )

    organization = create_organization(client)

    response = client.get(f"/api/v1/organizations/{organization['id']}/members")

    assert response.status_code == 200

    memberships = response.json()

    assert len(memberships) == 1
    assert memberships[0]["user_id"] == admin["id"]
    assert memberships[0]["role"] == "organization_admin"


def test_admin_can_add_worker(
    client: TestClient,
) -> None:
    register_user(
        client,
        "admin@example.com",
    )

    organization = create_organization(client)

    client.post("/api/v1/auth/logout")

    worker = register_user(
        client,
        "worker@example.com",
    )

    client.post("/api/v1/auth/logout")

    login_user(
        client,
        "admin@example.com",
    )

    response = client.post(
        (f"/api/v1/organizations/{organization['id']}/members"),
        json={
            "user_id": worker["id"],
            "role": "worker",
        },
    )

    assert response.status_code == 201
    assert response.json()["user_id"] == worker["id"]
    assert response.json()["role"] == "worker"


def test_worker_cannot_add_members(
    client: TestClient,
) -> None:
    register_user(
        client,
        "admin@example.com",
    )

    organization = create_organization(client)

    client.post("/api/v1/auth/logout")

    worker = register_user(
        client,
        "worker@example.com",
    )

    client.post("/api/v1/auth/logout")

    login_user(
        client,
        "admin@example.com",
    )

    add_response = client.post(
        (f"/api/v1/organizations/{organization['id']}/members"),
        json={
            "user_id": worker["id"],
            "role": "worker",
        },
    )

    assert add_response.status_code == 201

    client.post("/api/v1/auth/logout")

    login_user(
        client,
        "worker@example.com",
    )

    response = client.post(
        (f"/api/v1/organizations/{organization['id']}/members"),
        json={
            "user_id": ("00000000-0000-0000-0000-000000000001"),
            "role": "worker",
        },
    )

    assert response.status_code == 403

    assert response.json() == {"detail": ("Organization administrator permission required.")}


def test_member_can_list_members(
    client: TestClient,
) -> None:
    register_user(
        client,
        "admin@example.com",
    )

    organization = create_organization(client)

    client.post("/api/v1/auth/logout")

    worker = register_user(
        client,
        "worker@example.com",
    )

    client.post("/api/v1/auth/logout")

    login_user(
        client,
        "admin@example.com",
    )

    client.post(
        (f"/api/v1/organizations/{organization['id']}/members"),
        json={
            "user_id": worker["id"],
            "role": "worker",
        },
    )

    client.post("/api/v1/auth/logout")

    login_user(
        client,
        "worker@example.com",
    )

    response = client.get(f"/api/v1/organizations/{organization['id']}/members")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_outsider_cannot_list_members(
    client: TestClient,
) -> None:
    register_user(
        client,
        "admin@example.com",
    )

    organization = create_organization(client)

    client.post("/api/v1/auth/logout")

    register_user(
        client,
        "outsider@example.com",
    )

    response = client.get(f"/api/v1/organizations/{organization['id']}/members")

    assert response.status_code == 404


def test_duplicate_membership_returns_conflict(
    client: TestClient,
) -> None:
    register_user(
        client,
        "admin@example.com",
    )

    organization = create_organization(client)

    client.post("/api/v1/auth/logout")

    worker = register_user(
        client,
        "worker@example.com",
    )

    client.post("/api/v1/auth/logout")

    login_user(
        client,
        "admin@example.com",
    )

    payload = {
        "user_id": worker["id"],
        "role": "worker",
    }

    first_response = client.post(
        (f"/api/v1/organizations/{organization['id']}/members"),
        json=payload,
    )

    second_response = client.post(
        (f"/api/v1/organizations/{organization['id']}/members"),
        json=payload,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409
