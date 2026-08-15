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


def create_project(
    client: TestClient,
    organization_id: object,
) -> dict[str, object]:
    response = client.post(
        (f"/api/v1/organizations/{organization_id}/projects"),
        json={
            "name": "Prairie Ridge BESS",
            "code": "PR-BESS-01",
            "project_type": "battery_storage",
            "location": "Austin County, TX",
        },
    )

    assert response.status_code == 201

    return response.json()


def inspection_payload() -> dict[str, object]:
    return {
        "title": "Weekly Site Safety Inspection",
        "inspection_type": "weekly_site",
        "inspection_date": "2026-08-14",
        "notes": ("Initial walkthrough of active work areas."),
    }


def create_inspection(
    client: TestClient,
    organization_id: object,
    project_id: object,
):
    response = client.post(
        (f"/api/v1/organizations/{organization_id}/projects/{project_id}/inspections"),
        json=inspection_payload(),
    )

    assert response.status_code == 201

    return response


def test_inspection_creation_requires_authentication(
    client: TestClient,
) -> None:
    response = client.post(
        (
            "/api/v1/organizations/"
            "00000000-0000-0000-0000-000000000001/"
            "projects/"
            "00000000-0000-0000-0000-000000000002/"
            "inspections"
        ),
        json=inspection_payload(),
    )

    assert response.status_code == 401


def test_admin_can_create_inspection_draft(
    client: TestClient,
) -> None:
    admin = register_user(
        client,
        "admin@example.com",
    )

    organization = create_organization(client)

    project = create_project(
        client,
        organization["id"],
    )

    response = create_inspection(
        client,
        organization["id"],
        project["id"],
    )

    inspection = response.json()

    assert inspection["status"] == "draft"
    assert inspection["result"] is None
    assert inspection["submitted_at"] is None
    assert inspection["performed_by_user_id"] == admin["id"]


def test_member_can_list_project_inspections(
    client: TestClient,
) -> None:
    register_user(
        client,
        "admin@example.com",
    )

    organization = create_organization(client)

    project = create_project(
        client,
        organization["id"],
    )

    create_inspection(
        client,
        organization["id"],
        project["id"],
    )

    response = client.get(
        f"/api/v1/organizations/{organization['id']}/projects/{project['id']}/inspections"
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_inspection_can_be_updated_while_draft(
    client: TestClient,
) -> None:
    register_user(
        client,
        "admin@example.com",
    )

    organization = create_organization(client)

    project = create_project(
        client,
        organization["id"],
    )

    inspection = create_inspection(
        client,
        organization["id"],
        project["id"],
    ).json()

    response = client.patch(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects/"
            f"{project['id']}/inspections/"
            f"{inspection['id']}"
        ),
        json={
            "notes": "Updated field notes.",
        },
    )

    assert response.status_code == 200
    assert response.json()["notes"] == "Updated field notes."


def test_inspection_can_be_submitted(
    client: TestClient,
) -> None:
    register_user(
        client,
        "admin@example.com",
    )

    organization = create_organization(client)

    project = create_project(
        client,
        organization["id"],
    )

    inspection = create_inspection(
        client,
        organization["id"],
        project["id"],
    ).json()

    response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects/"
            f"{project['id']}/inspections/"
            f"{inspection['id']}/submit"
        ),
        json={
            "result": "needs_attention",
        },
    )

    assert response.status_code == 200

    submitted = response.json()

    assert submitted["status"] == "submitted"
    assert submitted["result"] == "needs_attention"
    assert submitted["submitted_at"] is not None


def test_submitted_inspection_cannot_be_edited(
    client: TestClient,
) -> None:
    register_user(
        client,
        "admin@example.com",
    )

    organization = create_organization(client)

    project = create_project(
        client,
        organization["id"],
    )

    inspection = create_inspection(
        client,
        organization["id"],
        project["id"],
    ).json()

    client.post(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects/"
            f"{project['id']}/inspections/"
            f"{inspection['id']}/submit"
        ),
        json={
            "result": "satisfactory",
        },
    )

    response = client.patch(
        (
            f"/api/v1/organizations/"
            f"{organization['id']}/projects/"
            f"{project['id']}/inspections/"
            f"{inspection['id']}"
        ),
        json={
            "notes": "Attempted edit.",
        },
    )

    assert response.status_code == 409


def test_inspection_cannot_be_submitted_twice(
    client: TestClient,
) -> None:
    register_user(
        client,
        "admin@example.com",
    )

    organization = create_organization(client)

    project = create_project(
        client,
        organization["id"],
    )

    inspection = create_inspection(
        client,
        organization["id"],
        project["id"],
    ).json()

    endpoint = (
        f"/api/v1/organizations/"
        f"{organization['id']}/projects/"
        f"{project['id']}/inspections/"
        f"{inspection['id']}/submit"
    )

    first_response = client.post(
        endpoint,
        json={
            "result": "satisfactory",
        },
    )

    second_response = client.post(
        endpoint,
        json={
            "result": "satisfactory",
        },
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 409


def test_inspection_lookup_is_tenant_scoped(
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

    first_project = create_project(
        client,
        first_organization["id"],
    )

    inspection = create_inspection(
        client,
        first_organization["id"],
        first_project["id"],
    ).json()

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

    second_project = create_project(
        client,
        second_organization["id"],
    )

    response = client.get(
        
            f"/api/v1/organizations/"
            f"{second_organization['id']}/projects/"
            f"{second_project['id']}/inspections/"
            f"{inspection['id']}"
        
    )

    assert response.status_code == 404


def test_worker_cannot_create_inspection(
    client: TestClient,
) -> None:
    admin = register_user(
        client,
        "admin@example.com",
    )

    organization = create_organization(client)

    project = create_project(
        client,
        organization["id"],
    )

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

    membership_response = client.post(
        (f"/api/v1/organizations/{organization['id']}/members"),
        json={
            "user_id": worker["id"],
            "role": "worker",
        },
    )

    assert membership_response.status_code == 201

    client.post("/api/v1/auth/logout")

    login_user(
        client,
        "worker@example.com",
    )

    response = client.post(
        (f"/api/v1/organizations/{organization['id']}/projects/{project['id']}/inspections"),
        json=inspection_payload(),
    )

    assert response.status_code == 403
