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
            "password": "gridguard-password-123",
        },
    )

    assert response.status_code == 201

    return response.json()


def create_organization(
    client: TestClient,
    name: str,
    slug: str,
):
    response = client.post(
        "/api/v1/organizations",
        json={
            "name": name,
            "slug": slug,
        },
    )

    assert response.status_code == 201

    return response


def test_create_organization_requires_authentication(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/organizations",
        json={
            "name": "Northstar Renewables",
            "slug": "northstar-renewables",
        },
    )

    assert response.status_code == 401


def test_authenticated_user_can_create_organization(
    client: TestClient,
) -> None:
    register_user(
        client,
        "admin@example.com",
    )

    response = create_organization(
        client,
        "Northstar Renewables",
        "northstar-renewables",
    )

    organization = response.json()

    assert organization["name"] == "Northstar Renewables"
    assert organization["slug"] == "northstar-renewables"
    assert organization["id"]


def test_user_can_get_own_organization(
    client: TestClient,
) -> None:
    register_user(
        client,
        "admin@example.com",
    )

    create_response = create_organization(
        client,
        "Northstar Renewables",
        "northstar-renewables",
    )

    organization_id = create_response.json()["id"]

    response = client.get(f"/api/v1/organizations/{organization_id}")

    assert response.status_code == 200
    assert response.json()["id"] == organization_id


def test_organization_list_is_scoped_to_current_user(
    client: TestClient,
) -> None:
    register_user(
        client,
        "first@example.com",
    )

    create_organization(
        client,
        "Northstar Renewables",
        "northstar-renewables",
    )

    client.post("/api/v1/auth/logout")

    register_user(
        client,
        "second@example.com",
    )

    create_organization(
        client,
        "Prairie Grid Services",
        "prairie-grid-services",
    )

    response = client.get("/api/v1/organizations")

    assert response.status_code == 200

    organizations = response.json()

    assert len(organizations) == 1
    assert organizations[0]["slug"] == "prairie-grid-services"


def test_cross_tenant_organization_access_is_hidden(
    client: TestClient,
) -> None:
    register_user(
        client,
        "first@example.com",
    )

    create_response = create_organization(
        client,
        "Northstar Renewables",
        "northstar-renewables",
    )

    organization_id = create_response.json()["id"]

    client.post("/api/v1/auth/logout")

    register_user(
        client,
        "outsider@example.com",
    )

    response = client.get(f"/api/v1/organizations/{organization_id}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Organization not found."}


def test_duplicate_organization_slug_returns_conflict(
    client: TestClient,
) -> None:
    register_user(
        client,
        "admin@example.com",
    )

    payload = {
        "name": "Northstar Renewables",
        "slug": "northstar-renewables",
    }

    first_response = client.post(
        "/api/v1/organizations",
        json=payload,
    )

    second_response = client.post(
        "/api/v1/organizations",
        json=payload,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_invalid_organization_slug_is_rejected(
    client: TestClient,
) -> None:
    register_user(
        client,
        "admin@example.com",
    )

    response = client.post(
        "/api/v1/organizations",
        json={
            "name": "Northstar Renewables",
            "slug": "Northstar Renewables!",
        },
    )

    assert response.status_code == 422


def test_organization_name_is_trimmed(
    client: TestClient,
) -> None:
    register_user(
        client,
        "admin@example.com",
    )

    response = client.post(
        "/api/v1/organizations",
        json={
            "name": "   Northstar Renewables   ",
            "slug": "northstar-renewables",
        },
    )

    assert response.status_code == 201

    assert response.json()["name"] == "Northstar Renewables"
