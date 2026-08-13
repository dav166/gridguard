from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

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

    def override_get_db() -> Generator[Session, None, None]:
        with testing_session_local() as session:
            yield session

    application.dependency_overrides[get_db] = override_get_db

    with TestClient(application) as test_client:
        yield test_client

    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def test_create_organization(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/organizations",
        json={
            "name": "Northstar Renewables",
            "slug": "northstar-renewables",
        },
    )

    assert response.status_code == 201

    organization = response.json()

    assert organization["name"] == "Northstar Renewables"
    assert organization["slug"] == "northstar-renewables"
    assert organization["id"]
    assert organization["created_at"]
    assert organization["updated_at"]


def test_get_organization(
    client: TestClient,
) -> None:
    create_response = client.post(
        "/api/v1/organizations",
        json={
            "name": "Northstar Renewables",
            "slug": "northstar-renewables",
        },
    )

    assert create_response.status_code == 201

    organization_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/organizations/{organization_id}"
    )

    assert response.status_code == 200
    assert response.json()["id"] == organization_id
    assert response.json()["name"] == "Northstar Renewables"


def test_list_organizations(
    client: TestClient,
) -> None:
    first_response = client.post(
        "/api/v1/organizations",
        json={
            "name": "Northstar Renewables",
            "slug": "northstar-renewables",
        },
    )

    second_response = client.post(
        "/api/v1/organizations",
        json={
            "name": "Prairie Grid Services",
            "slug": "prairie-grid-services",
        },
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201

    response = client.get("/api/v1/organizations")

    assert response.status_code == 200

    organizations = response.json()

    assert len(organizations) == 2

    slugs = {
        organization["slug"]
        for organization in organizations
    }

    assert slugs == {
        "northstar-renewables",
        "prairie-grid-services",
    }


def test_duplicate_organization_slug_returns_conflict(
    client: TestClient,
) -> None:
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

    assert second_response.json() == {
        "detail": "An organization with this slug already exists."
    }


def test_invalid_organization_slug_is_rejected(
    client: TestClient,
) -> None:
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
    response = client.post(
        "/api/v1/organizations",
        json={
            "name": "   Northstar Renewables   ",
            "slug": "northstar-renewables",
        },
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Northstar Renewables"


def test_missing_organization_returns_not_found(
    client: TestClient,
) -> None:
    response = client.get(
        "/api/v1/organizations/"
        "00000000-0000-0000-0000-000000000000"
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Organization not found."
    }