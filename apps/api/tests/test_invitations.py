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


def create_invitation(
    client: TestClient,
    organization_id: object,
    email: str = "worker@example.com",
    role: str = "worker",
):
    response = client.post(
        (f"/api/v1/organizations/{organization_id}/invitations"),
        json={
            "email": email,
            "role": role,
        },
    )

    assert response.status_code == 201

    return response


def test_admin_can_create_invitation(
    client: TestClient,
) -> None:
    register_user(
        client,
        "admin@example.com",
    )

    organization = create_organization(client)

    response = create_invitation(
        client,
        organization["id"],
    )

    invitation = response.json()

    assert invitation["email"] == "worker@example.com"
    assert invitation["role"] == "worker"
    assert invitation["token"]
    assert "token_hash" not in invitation


def test_pending_invitation_list_does_not_expose_token(
    client: TestClient,
) -> None:
    register_user(
        client,
        "admin@example.com",
    )

    organization = create_organization(client)

    create_invitation(
        client,
        organization["id"],
    )

    response = client.get(f"/api/v1/organizations/{organization['id']}/invitations")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert "token" not in response.json()[0]
    assert "token_hash" not in response.json()[0]


def test_duplicate_pending_invitation_returns_conflict(
    client: TestClient,
) -> None:
    register_user(
        client,
        "admin@example.com",
    )

    organization = create_organization(client)

    create_invitation(
        client,
        organization["id"],
    )

    response = client.post(
        (f"/api/v1/organizations/{organization['id']}/invitations"),
        json={
            "email": "worker@example.com",
            "role": "worker",
        },
    )

    assert response.status_code == 409


def test_invited_user_can_accept_invitation(
    client: TestClient,
) -> None:
    register_user(
        client,
        "admin@example.com",
    )

    organization = create_organization(client)

    invitation_response = create_invitation(
        client,
        organization["id"],
        email="worker@example.com",
        role="supervisor",
    )

    token = invitation_response.json()["token"]

    client.post("/api/v1/auth/logout")

    register_user(
        client,
        "worker@example.com",
    )

    response = client.post(
        "/api/v1/invitations/accept",
        json={
            "token": token,
        },
    )

    assert response.status_code == 200

    membership = response.json()

    assert membership["organization_id"] == organization["id"]

    assert membership["role"] == "supervisor"

    organizations_response = client.get("/api/v1/organizations")

    assert organizations_response.status_code == 200

    assert [organization["id"] for organization in organizations_response.json()] == [
        organization["id"]
    ]


def test_different_user_cannot_accept_invitation(
    client: TestClient,
) -> None:
    register_user(
        client,
        "admin@example.com",
    )

    organization = create_organization(client)

    invitation_response = create_invitation(
        client,
        organization["id"],
    )

    token = invitation_response.json()["token"]

    client.post("/api/v1/auth/logout")

    register_user(
        client,
        "someone-else@example.com",
    )

    response = client.post(
        "/api/v1/invitations/accept",
        json={
            "token": token,
        },
    )

    assert response.status_code == 403


def test_invitation_cannot_be_accepted_twice(
    client: TestClient,
) -> None:
    register_user(
        client,
        "admin@example.com",
    )

    organization = create_organization(client)

    invitation_response = create_invitation(
        client,
        organization["id"],
    )

    token = invitation_response.json()["token"]

    client.post("/api/v1/auth/logout")

    register_user(
        client,
        "worker@example.com",
    )

    first_response = client.post(
        "/api/v1/invitations/accept",
        json={
            "token": token,
        },
    )

    second_response = client.post(
        "/api/v1/invitations/accept",
        json={
            "token": token,
        },
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 404


def test_worker_cannot_create_invitation(
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
        (f"/api/v1/organizations/{organization['id']}/invitations"),
        json={
            "email": "new-worker@example.com",
            "role": "worker",
        },
    )

    assert response.status_code == 403
