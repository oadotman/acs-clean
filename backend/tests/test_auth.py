import pytest
from fastapi.testclient import TestClient


def test_user_registration_success(client: TestClient, sample_user_data: dict):
    """Test successful user registration."""
    response = client.post("/api/auth/register", json=sample_user_data)
    assert response.status_code == 201
    
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == sample_user_data["email"]
    assert data["user"]["full_name"] == sample_user_data["full_name"]


def test_user_registration_duplicate_email(client: TestClient, sample_user_data: dict):
    """Test registration with duplicate email."""
    # Register first user
    client.post("/api/auth/register", json=sample_user_data)
    
    # Try to register with same email
    response = client.post("/api/auth/register", json=sample_user_data)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


def test_user_registration_invalid_email(client: TestClient, sample_user_data: dict):
    """Test registration with invalid email."""
    sample_user_data["email"] = "invalid-email"
    response = client.post("/api/auth/register", json=sample_user_data)
    assert response.status_code == 422


def test_user_registration_weak_password(client: TestClient, sample_user_data: dict):
    """Test registration with weak password."""
    sample_user_data["password"] = "123"
    response = client.post("/api/auth/register", json=sample_user_data)
    assert response.status_code == 422


def test_user_login_success(client: TestClient, sample_user_data: dict):
    """Test successful user login."""
    # Register user first
    client.post("/api/auth/register", json=sample_user_data)
    
    # Login
    login_data = {
        "username": sample_user_data["email"],
        "password": sample_user_data["password"]
    }
    response = client.post("/api/auth/token", data=login_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_user_login_invalid_credentials(client: TestClient, sample_user_data: dict):
    """Test login with invalid credentials."""
    # Register user first
    client.post("/api/auth/register", json=sample_user_data)
    
    # Try login with wrong password
    login_data = {
        "username": sample_user_data["email"],
        "password": "wrongpassword"
    }
    response = client.post("/api/auth/token", data=login_data)
    assert response.status_code == 401


def test_user_login_nonexistent_user(client: TestClient):
    """Test login with nonexistent user."""
    login_data = {
        "username": "nonexistent@example.com",
        "password": "somepassword"
    }
    response = client.post("/api/auth/token", data=login_data)
    assert response.status_code == 401


def test_get_current_user_success(client: TestClient, authenticated_headers: dict):
    """Test getting current user information."""
    response = client.get("/api/auth/me", headers=authenticated_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "email" in data
    assert "full_name" in data
    assert "subscription_tier" in data


def test_get_current_user_no_token(client: TestClient):
    """Test getting current user without token."""
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_get_current_user_invalid_token(client: TestClient):
    """Test getting current user with invalid token."""
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/api/auth/me", headers=headers)
    assert response.status_code == 401


def test_protected_route_access(client: TestClient, authenticated_headers: dict):
    """Test accessing protected routes with valid token."""
    response = client.get("/api/ads/history", headers=authenticated_headers)
    assert response.status_code == 200


def test_protected_route_no_access(client: TestClient):
    """Test accessing protected routes without token."""
    response = client.get("/api/ads/history")
    assert response.status_code == 401
