
def test_register_user(client):
    response = client.post(
        "/auth/register",
        json={
            "email": "learner@example.com",
            "password": "LearningFastAPI123!",
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["email"] == "learner@example.com"
    assert isinstance(data["id"], int)
    assert data["is_active"] is True

    # Sensitive password information must never be returned.
    assert "password" not in data
    assert "password_hash" not in data


def test_register_duplicate_email(client):
    payload = {
        "email": "learner@example.com",
        "password": "LearningFastAPI123!",
    }

    first_response = client.post("/auth/register", json=payload)
    second_response = client.post("/auth/register", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Email is already registered"


def test_register_invalid_email(client):
    response = client.post(
        "/auth/register",
        json={
            "email": "not-an-email",
            "password": "LearningFastAPI123!",
        },
    )

    assert response.status_code == 422


def test_register_short_password(client):
    response = client.post(
        "/auth/register",
        json={
            "email": "learner@example.com",
            "password": "short",
        },
    )

    assert response.status_code == 422

def test_get_current_user(client, auth_headers):
    response = client.get("/auth/me", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert data["is_active"] is True
    assert "password_hash" not in data


def test_get_current_user_without_token(client):
    response = client.get("/auth/me")

    assert response.status_code == 401