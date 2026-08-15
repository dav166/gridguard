from fastapi.testclient import TestClient

PASSWORD = "gridguard-password-123"


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
    name: str = "Northstar Renewables",
    slug: str = "northstar-renewables",
) -> dict[str, object]:
    response = client.post(
        "/api/v1/organizations",
        json={
            "name": name,
            "slug": slug,
        },
    )

    assert response.status_code == 201

    return response.json()


def project_payload() -> dict[str, object]:
    return {
        "name": "Prairie Ridge BESS",
        "code": "PR-BESS-01",
        "project_type": "battery_storage",
        "location": "Austin County, TX",
        "description": ("Utility-scale battery storage project."),
        "start_date": "2026-08-01",
        "end_date": "2027-04-30",
    }


def test_project_creation_requires_authentication(
    client: TestClient,
) -> None:
    response = client.post(
        ("/api/v1/organizations/00000000-0000-0000-0000-000000000001/projects"),
        json=project_payload(),
    )

    assert response.status_code == 401


def test_admin_can_create_project(
    client: TestClient,
) -> None:
    register_user(
        client,
        "admin@example.com",
    )

    organization = create_organization(client)

    response = client.post(
        (f"/api/v1/organizations/{organization['id']}/projects"),
        json=project_payload(),
    )

    assert response.status_code == 201

    project = response.json()

    assert project["name"] == "Prairie Ridge BESS"
    assert project["code"] == "PR-BESS-01"
    assert project["status"] == "planned"
    assert project["project_type"] == "battery_storage"
    assert project["organization_id"] == organization["id"]


def test_worker_cannot_create_project(
    client: TestClient,
) -> None:
    admin = register_user(
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
        str(admin["email"]),
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
        (f"/api/v1/organizations/{organization['id']}/projects"),
        json=project_payload(),
    )

    assert response.status_code == 403


def test_member_can_list_projects(
    client: TestClient,
) -> None:
    register_user(
        client,
        "admin@example.com",
    )

    organization = create_organization(client)

    client.post(
        (f"/api/v1/organizations/{organization['id']}/projects"),
        json=project_payload(),
    )

    response = client.get(f"/api/v1/organizations/{organization['id']}/projects")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_project_lookup_is_tenant_scoped(
    client: TestClient,
) -> None:
    register_user(
        client,
        "first@example.com",
    )

    first_organization = create_organization(
        client,
        "Northstar Renewables",
        "northstar-renewables",
    )

    project_response = client.post(
        (f"/api/v1/organizations/{first_organization['id']}/projects"),
        json=project_payload(),
    )

    assert project_response.status_code == 201

    project_id = project_response.json()["id"]

    client.post("/api/v1/auth/logout")

    register_user(
        client,
        "second@example.com",
    )

    second_organization = create_organization(
        client,
        "Prairie Grid Services",
        "prairie-grid-services",
    )

    response = client.get(
        f"/api/v1/organizations/{second_organization['id']}/projects/{project_id}"
    )

    assert response.status_code == 404


def test_duplicate_project_code_returns_conflict(
    client: TestClient,
) -> None:
    register_user(
        client,
        "admin@example.com",
    )

    organization = create_organization(client)

    first_response = client.post(
        (f"/api/v1/organizations/{organization['id']}/projects"),
        json=project_payload(),
    )

    second_response = client.post(
        (f"/api/v1/organizations/{organization['id']}/projects"),
        json=project_payload(),
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_project_code_is_normalized(
    client: TestClient,
) -> None:
    register_user(
        client,
        "admin@example.com",
    )

    organization = create_organization(client)

    payload = project_payload()
    payload["code"] = "pr-bess-01"

    response = client.post(
        (f"/api/v1/organizations/{organization['id']}/projects"),
        json=payload,
    )

    assert response.status_code == 201
    assert response.json()["code"] == "PR-BESS-01"


def test_project_status_can_be_updated(
    client: TestClient,
) -> None:
    register_user(
        client,
        "admin@example.com",
    )

    organization = create_organization(client)

    create_response = client.post(
        (f"/api/v1/organizations/{organization['id']}/projects"),
        json=project_payload(),
    )

    project_id = create_response.json()["id"]

    response = client.patch(
        (f"/api/v1/organizations/{organization['id']}/projects/{project_id}"),
        json={
            "status": "active",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "active"


def test_invalid_project_date_range_is_rejected(
    client: TestClient,
) -> None:
    register_user(
        client,
        "admin@example.com",
    )

    organization = create_organization(client)

    payload = project_payload()
    payload["start_date"] = "2027-01-01"
    payload["end_date"] = "2026-01-01"

    response = client.post(
        (f"/api/v1/organizations/{organization['id']}/projects"),
        json=payload,
    )

    assert response.status_code == 422
