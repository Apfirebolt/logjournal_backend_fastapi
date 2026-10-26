import pytest
from auth import hashing


def test_register_user_success(client):
    """Test successful user registration (matches /api/auth/register)"""
    payload = {
        "username": "alice",
        "email": "alice@example.com",
        "password": "SecurePassword123"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == payload["email"]
    assert data["username"] == payload["username"]
    assert "id" in data


def test_register_duplicate_email_fails(client):
    """Test duplicate registration returns 400 error via validator check"""
    payload = {
        "username": "alice1",
        "email": "alice@example.com",
        "password": "Password123"
    }
    client.post("/api/auth/register", json=payload)

    # Attempt second registration with same email
    response = client.post("/api/auth/register", json={
        "username": "alice2",
        "email": "alice@example.com",
        "password": "DifferentPassword123"
    })
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()


def test_get_all_users_and_root(client):
    """Test both GET /api/auth/users and GET /api/auth/ endpoints"""
    client.post("/api/auth/register", json={
        "username": "user1",
        "email": "user1@example.com",
        "password": "Password123"
    })

    # Test /api/auth/users
    res1 = client.get("/api/auth/users")
    assert res1.status_code == 200
    assert len(res1.json()) >= 1

    # Test root /api/auth/
    res2 = client.get("/api/auth/")
    assert res2.status_code == 200
    assert len(res2.json()) >= 1


def test_login_missing_fields_fails(client):
    """Test login with empty email or password returns 400"""
    response = client.post("/api/auth/login", json={"email": "", "password": ""})
    assert response.status_code == 400
    assert "Email and password are required" in response.json()["detail"]


def test_login_user_not_found(client):
    """Test login with non-existent email returns 404"""
    response = client.post("/api/auth/login", json={
        "email": "ghost@example.com",
        "password": "Password123"
    })
    assert response.status_code == 404
    assert "User not found" in response.json()["detail"]


def test_login_invalid_password(client):
    """Test login with wrong password returns 400"""
    client.post("/api/auth/register", json={
        "username": "bob",
        "email": "bob@example.com",
        "password": "Password123"
    })

    response = client.post("/api/auth/login", json={
        "email": "bob@example.com",
        "password": "WrongPassword"
    })
    assert response.status_code == 400
    assert "Invalid Password" in response.json()["detail"]


def test_login_success_and_token_generation(client):
    """Test successful login returns JWT bearer token and user metadata"""
    client.post("/api/auth/register", json={
        "username": "charlie",
        "email": "charlie@example.com",
        "password": "Password123"
    })

    response = client.post("/api/auth/login", json={
        "email": "charlie@example.com",
        "password": "Password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "charlie@example.com"


def test_get_profile_and_me_endpoints(client):
    """Test protected endpoints GET /api/auth/profile and GET /api/auth/me"""
    client.post("/api/auth/register", json={
        "username": "dave",
        "email": "dave@example.com",
        "password": "Password123"
    })
    login_res = client.post("/api/auth/login", json={
        "email": "dave@example.com",
        "password": "Password123"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Test /me
    me_res = client.get("/api/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "dave@example.com"

    # Test /profile
    profile_res = client.get("/api/auth/profile", headers=headers)
    assert profile_res.status_code == 200
    assert profile_res.json()["email"] == "dave@example.com"


def test_unauthorized_access_fails(client):
    """Test accessing protected route without a token fails"""
    response = client.get("/api/auth/me")
    assert response.status_code in [401, 403]