import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


@pytest.fixture(scope="module")
def auth_token():
    """Helper fixture to log in and get a valid JWT bearer token"""
    response = client.post(
        "/api/auth/login", json={"email": "ash@gmail.com", "password": "pass123"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    return data.get("access_token") or data.get("token")


def test_get_categories_unauthorized():
    """Test that fetching categories without a token returns 401"""
    response = client.get("/api/journal/categories")
    assert response.status_code == 401


def test_get_categories_with_token(auth_token):
    """Test fetching system default and custom categories"""
    response = client.get(
        "/api/journal/categories",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_create_custom_category(auth_token):
    """Test allowing a user to add a custom category (e.g., 'Friends')"""
    response = client.post(
        "/api/journal/categories",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"name": "Friends"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Friends"
    assert data["is_default"] == 0
    assert "id" in data


def test_create_journal_entry(auth_token):
    """Test creating a daily journal entry with global prompts and category ratings/content"""
    # 1. Create a custom category to use in the entry
    cat_res = client.post(
        "/api/journal/categories",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"name": "Coding"}
    )
    category_id = cat_res.json()["id"]

    # 2. Submit journal entry payload
    payload = {
        "title": "A Very Productive Day",
        "highlights": "<p>Finished implementing the journal module backend.</p>",
        "gratitude": {"text": "Grateful for good coffee and robust test suites."},
        "better_day_thoughts": "<p>Could have taken short breaks in between.</p>",
        "category_sections": [
            {
                "category_id": category_id,
                "content": "<p>Wrote clean threadpool wrappers for SQLAlchemy.</p>",
                "rating_score": 4.5
            }
        ]
    }

    response = client.post(
        "/api/journal/entries",
        headers={"Authorization": f"Bearer {auth_token}"},
        json=payload
    )
    assert response.status_code == 201
    data = response.json()

    assert data["title"] == "A Very Productive Day"
    assert data["highlights"] == "<p>Finished implementing the journal module backend.</p>"
    assert len(data["category_sections"]) == 1
    assert data["category_sections"][0]["rating_score"] == 4.5
    assert data["category_sections"][0]["category_name"] == "Coding"


def test_list_journal_entries(auth_token):
    """Test retrieving all journal entries for the authenticated user"""
    response = client.get(
        "/api/journal/entries",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_journal_entry_detail(auth_token):
    """Test fetching a specific journal entry by ID"""
    # Create an entry first
    payload = {
        "title": "Detail Test Entry",
        "highlights": "Quick test highlight",
        "category_sections": []
    }
    create_res = client.post(
        "/api/journal/entries",
        headers={"Authorization": f"Bearer {auth_token}"},
        json=payload
    )
    entry_id = create_res.json()["id"]

    # Fetch detail
    response = client.get(
        f"/api/journal/entries/{entry_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Detail Test Entry"


def test_get_nonexistent_entry_returns_404(auth_token):
    """Test 404 response when querying an invalid entry ID"""
    response = client.get(
        "/api/journal/entries/99999",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Journal entry not found"