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


def create_inspection(
    client: TestClient,
    organization_id: object,
    project_id: object,
) -> dict[str, object]:
    response = client.post(
        (f"/api/v1/organizations/{organization_id}/projects/{project_id}/inspections"),
        json={
            "title": "Weekly Site Safety Inspection",
            "inspection_type": "weekly_site",
            "inspection_date": "2026-08-14",
        },
    )

    assert response.status_code == 201

    return response.json()


def unsafe_observation_payload() -> dict[str, object]:
    return {
        "kind": "unsafe_condition",
        "category": "electrical",
        "severity": "high",
        "location": "BESS Block 4",
        "description": ("Electrical cabinet left open and unattended."),
        "immediate_action_taken": ("Area barricaded and supervisor notified."),
    }


def observation_endpoint(
    organization_id: object,
    project_id: object,
    inspection_id: object,
) -> str:
    return (
        f"/api/v1/organizations/"
        f"{organization_id}/projects/"
        f"{project_id}/inspections/"
        f"{inspection_id}/observations"
    )


def test_admin_can_create_unsafe_observation(
    client: TestClient,
) -> None:
    user = register_user(
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
    )

    response = client.post(
        observation_endpoint(
            organization["id"],
            project["id"],
            inspection["id"],
        ),
        json=unsafe_observation_payload(),
    )

    assert response.status_code == 201

    observation = response.json()

    assert observation["kind"] == "unsafe_condition"
    assert observation["severity"] == "high"

    assert observation["created_by_user_id"] == user["id"]


def test_high_severity_requires_corrective_action(
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
    )

    response = client.post(
        observation_endpoint(
            organization["id"],
            project["id"],
            inspection["id"],
        ),
        json=unsafe_observation_payload(),
    )

    assert response.status_code == 201

    assert response.json()["requires_corrective_action"] is True


def test_safe_practice_has_no_severity(
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
    )

    response = client.post(
        observation_endpoint(
            organization["id"],
            project["id"],
            inspection["id"],
        ),
        json={
            "kind": "safe_practice",
            "category": "ppe",
            "location": "Laydown yard",
            "description": ("Crew maintained full PPE compliance."),
        },
    )

    assert response.status_code == 201
    assert response.json()["severity"] is None

    assert response.json()["requires_corrective_action"] is False


def test_unsafe_observation_requires_severity(
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
    )

    response = client.post(
        observation_endpoint(
            organization["id"],
            project["id"],
            inspection["id"],
        ),
        json={
            "kind": "unsafe_condition",
            "category": "electrical",
            "location": "BESS Block 4",
            "description": "Open electrical cabinet.",
        },
    )

    assert response.status_code == 422


def test_safe_practice_rejects_severity(
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
    )

    response = client.post(
        observation_endpoint(
            organization["id"],
            project["id"],
            inspection["id"],
        ),
        json={
            "kind": "safe_practice",
            "category": "ppe",
            "severity": "low",
            "location": "Laydown yard",
            "description": "Strong PPE compliance.",
        },
    )

    assert response.status_code == 422


def test_observations_can_be_listed(
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
    )

    endpoint = observation_endpoint(
        organization["id"],
        project["id"],
        inspection["id"],
    )

    client.post(
        endpoint,
        json=unsafe_observation_payload(),
    )

    response = client.get(endpoint)

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_observation_can_be_updated_while_draft(
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
    )

    endpoint = observation_endpoint(
        organization["id"],
        project["id"],
        inspection["id"],
    )

    observation = client.post(
        endpoint,
        json=unsafe_observation_payload(),
    ).json()

    response = client.patch(
        f"{endpoint}/{observation['id']}",
        json={
            "location": "BESS Block 5",
            "severity": "critical",
        },
    )

    assert response.status_code == 200
    assert response.json()["location"] == "BESS Block 5"
    assert response.json()["severity"] == "critical"

    assert response.json()["requires_corrective_action"] is True


def test_submitted_inspection_rejects_new_observation(
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
    )

    client.post(
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

    response = client.post(
        observation_endpoint(
            organization["id"],
            project["id"],
            inspection["id"],
        ),
        json=unsafe_observation_payload(),
    )

    assert response.status_code == 409


def test_submitted_inspection_rejects_observation_edit(
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
    )

    endpoint = observation_endpoint(
        organization["id"],
        project["id"],
        inspection["id"],
    )

    observation = client.post(
        endpoint,
        json=unsafe_observation_payload(),
    ).json()

    client.post(
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

    response = client.patch(
        f"{endpoint}/{observation['id']}",
        json={
            "location": "Changed after submission",
        },
    )

    assert response.status_code == 409


def test_observation_lookup_is_tenant_scoped(
    client: TestClient,
) -> None:
    register_user(
        client,
        "first@example.com",
    )

    first_organization = create_organization(client)

    first_project = create_project(
        client,
        first_organization["id"],
    )

    first_inspection = create_inspection(
        client,
        first_organization["id"],
        first_project["id"],
    )

    first_endpoint = observation_endpoint(
        first_organization["id"],
        first_project["id"],
        first_inspection["id"],
    )

    observation = client.post(
        first_endpoint,
        json=unsafe_observation_payload(),
    ).json()

    client.post("/api/v1/auth/logout")

    register_user(
        client,
        "second@example.com",
    )

    second_organization = client.post(
        "/api/v1/organizations",
        json={
            "name": "Prairie Grid Services",
            "slug": "prairie-grid-services",
        },
    ).json()

    second_project = create_project(
        client,
        second_organization["id"],
    )

    second_inspection = create_inspection(
        client,
        second_organization["id"],
        second_project["id"],
    )

    response = client.get(
        
            f"{
                observation_endpoint(
                    second_organization['id'],
                    second_project['id'],
                    second_inspection['id'],
                )
            }/{observation['id']}"
        
    )

    assert response.status_code == 404
