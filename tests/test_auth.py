import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


@pytest.fixture(scope="module")
def auth_token():
    response = client.post(
        "/api/auth/login", json={"email": "ash@gmail.com", "password": "pass123"}
    )
    assert response.status_code == 200, response.text
    return response.json().get("access_token") or response.json().get("token")


def test_register():
    # First registration should succeed (201 Created)
    response = client.post(
        "/api/auth/register",
        json={
            "username": "newtestuser",
            "email": "unique_test@example.com",
            "password": "testpassword",
        },
    )
    assert response.status_code == 201

    # Second registration with the same email should fail (400 Bad Request)
    response_duplicate = client.post(
        "/api/auth/register",
        json={
            "username": "newtestuser2",
            "email": "unique_test@example.com",
            "password": "testpassword",
        },
    )
    assert response_duplicate.status_code == 400


def test_login():
    response = client.post(
        "/api/auth/login", json={"email": "ash@gmail.com", "password": "pass123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data or "token" in data


def test_invalid_login_empty_fields():
    response = client.post("/api/auth/login", json={"email": "", "password": ""})
    assert response.status_code in [400, 422]


def test_invalid_login_wrong_password():
    response = client.post(
        "/api/auth/login", json={"email": "ash@gmail.com", "password": "wrongpass"}
    )
    assert response.status_code in [400, 401]


def test_register_missing_fields():
    response = client.post(
        "/api/auth/register",
        json={
            "username": "",
            "email": "",
            "password": "",
        },
    )
    assert response.status_code in [400, 422]


def test_register_invalid_email():
    response = client.post(
        "/api/auth/register",
        json={
            "username": "user2",
            "email": "not-an-email",
            "password": "password123",
        },
    )
    assert response.status_code in [400, 422]


def test_get_profile_no_token():
    response = client.get("/api/auth/profile")
    assert response.status_code == 401


def test_get_profile_invalid_token():
    response = client.get(
        "/api/auth/profile", headers={"Authorization": "Bearer invalidtoken"}
    )
    assert response.status_code == 401


def test_get_profile_with_token(auth_token):
    response = client.get(
        "/api/auth/profile", headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "ash@gmail.com"
    assert "username" in data


def test_get_me_with_token(auth_token):
    response = client.get(
        "/api/auth/me", headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "ash@gmail.com"
    assert "username" in data


def test_get_all_users(auth_token):
    response = client.get("/api/auth", headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for user in data:
        assert "id" in user
        assert "username" in user
        assert "email" in user