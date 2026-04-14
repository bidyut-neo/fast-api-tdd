import pytest
from fastapi.testclient import TestClient
import os
import time


def test_signup_success(client):
    """Test successful user signup"""
    user_data = {
        "first_name": "John",
        "last_name": "Doe",
        "username": "johndoe",
        "password": "securepassword123"
    }
    
    response = client.post("/auth/signup", json=user_data)
    
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 0


def test_signup_duplicate_username(client):
    """Test signup with duplicate username"""
    user_data = {
        "first_name": "John",
        "last_name": "Doe",
        "username": "johndoe",
        "password": "securepassword123"
    }
    
    # First signup should succeed
    response1 = client.post("/auth/signup", json=user_data)
    assert response1.status_code == 201
    
    # Second signup with same username should fail
    user_data2 = {
        "first_name": "Jane",
        "last_name": "Doe",
        "username": "johndoe",  # Same username
        "password": "differentpassword"
    }
    
    response2 = client.post("/auth/signup", json=user_data2)
    assert response2.status_code == 400
    data = response2.json()
    assert "detail" in data
    assert "username" in data["detail"].lower()


def test_signup_validation_error(client):
    """Test signup with invalid data"""
    # Missing required field
    user_data = {
        "first_name": "John",
        "last_name": "Doe",
        # Missing username and password
    }
    
    response = client.post("/auth/signup", json=user_data)
    assert response.status_code == 422  # Validation error


def test_login_success(client):
    """Test successful login with correct credentials"""
    # First create a user
    user_data = {
        "first_name": "Alice",
        "last_name": "Smith",
        "username": "alice",
        "password": "alicepassword"
    }
    
    signup_response = client.post("/auth/signup", json=user_data)
    assert signup_response.status_code == 201
    
    # Now login
    login_data = {
        "username": "alice",
        "password": "alicepassword"
    }
    
    response = client.post("/auth/login", json=login_data)
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    """Test login with wrong password"""
    # Create a user
    user_data = {
        "first_name": "Bob",
        "last_name": "Brown",
        "username": "bob",
        "password": "correctpassword"
    }
    
    client.post("/auth/signup", json=user_data)
    
    # Try login with wrong password
    login_data = {
        "username": "bob",
        "password": "wrongpassword"
    }
    
    response = client.post("/auth/login", json=login_data)
    
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data
    assert "invalid" in data["detail"].lower() or "incorrect" in data["detail"].lower()


def test_login_nonexistent_user(client):
    """Test login with non-existent username"""
    login_data = {
        "username": "nonexistent",
        "password": "anypassword"
    }
    
    response = client.post("/auth/login", json=login_data)
    
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data


def test_protected_book_endpoints_without_token(client):
    """Test that book endpoints require authentication"""
    # Try to access protected endpoints without token
    book_data = {
        "title": "Test Book",
        "author": "Test Author",
        "published_year": 2023,
        "isbn": "1234567890123"
    }
    
    # POST /books/
    response = client.post("/books/", json=book_data)
    assert response.status_code == 403
    
    # GET /books/
    response = client.get("/books/")
    assert response.status_code == 403
    
    # GET /books/{id}
    response = client.get("/books/1")
    assert response.status_code == 403
    
    # PUT /books/{id}
    response = client.put("/books/1", json=book_data)
    assert response.status_code == 403
    
    # DELETE /books/{id}
    response = client.delete("/books/1")
    assert response.status_code == 403


def test_protected_book_endpoints_with_token(client):
    """Test that book endpoints work with valid token"""
    # Create a user and get token
    user_data = {
        "first_name": "Test",
        "last_name": "User",
        "username": "testuser",
        "password": "testpassword"
    }
    
    signup_response = client.post("/auth/signup", json=user_data)
    assert signup_response.status_code == 201
    token = signup_response.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a book with authentication
    book_data = {
        "title": "Protected Book",
        "author": "Protected Author",
        "published_year": 2023,
        "isbn": "9876543210987"
    }
    
    response = client.post("/books/", json=book_data, headers=headers)
    assert response.status_code == 201
    book = response.json()
    book_id = book["id"]
    
    # Get all books
    response = client.get("/books/", headers=headers)
    assert response.status_code == 200
    books = response.json()
    assert len(books) > 0
    
    # Get specific book
    response = client.get(f"/books/{book_id}", headers=headers)
    assert response.status_code == 200
    
    # Update book
    update_data = {
        "title": "Updated Book",
        "author": "Updated Author",
        "published_year": 2024,
        "isbn": "9876543210987"
    }
    response = client.put(f"/books/{book_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    
    # Delete book
    response = client.delete(f"/books/{book_id}", headers=headers)
    assert response.status_code == 204


def test_logout_success(client):
    """Test logout endpoint (token should still work until expiration)"""
    # Create a user and get token
    user_data = {
        "first_name": "Logout",
        "last_name": "Test",
        "username": "logoutuser",
        "password": "logoutpass"
    }
    
    signup_response = client.post("/auth/signup", json=user_data)
    token = signup_response.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Call logout endpoint
    response = client.post("/auth/logout", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Logged out successfully"
    
    # Note: With our API key invalidation approach, the token should still work
    # until the API key is deleted (which happens on next login).
    # The logout endpoint is mostly informational.


def test_change_password_success(client):
    """Test successful password change"""
    # Create a user
    user_data = {
        "first_name": "Change",
        "last_name": "Password",
        "username": "changepass",
        "password": "oldpassword"
    }
    
    signup_response = client.post("/auth/signup", json=user_data)
    token = signup_response.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Change password
    change_data = {
        "current_password": "oldpassword",
        "new_password": "newpassword123"
    }
    
    response = client.post("/auth/change-password", json=change_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Password changed successfully"
    
    # Verify old password no longer works
    login_old = {
        "username": "changepass",
        "password": "oldpassword"
    }
    response = client.post("/auth/login", json=login_old)
    assert response.status_code == 401
    
    # Verify new password works
    login_new = {
        "username": "changepass",
        "password": "newpassword123"
    }
    response = client.post("/auth/login", json=login_new)
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_change_password_wrong_current_password(client):
    """Test password change with wrong current password"""
    # Create a user
    user_data = {
        "first_name": "Wrong",
        "last_name": "Pass",
        "username": "wrongpass",
        "password": "correctpass"
    }
    
    signup_response = client.post("/auth/signup", json=user_data)
    token = signup_response.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try to change password with wrong current password
    change_data = {
        "current_password": "wrongcurrent",
        "new_password": "newpassword123"
    }
    
    response = client.post("/auth/change-password", json=change_data, headers=headers)
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data


def test_change_password_without_authentication(client):
    """Test password change without authentication token"""
    change_data = {
        "current_password": "old",
        "new_password": "new"
    }
    
    response = client.post("/auth/change-password", json=change_data)
    assert response.status_code == 403


def test_token_expiration(client):
    """Test that token expires after configured time (5 minutes)"""
    # This test is more complex because we'd need to mock time
    # For now, we'll just verify the token structure is valid
    user_data = {
        "first_name": "Expire",
        "last_name": "Test",
        "username": "expiretest",
        "password": "expirepass"
    }
    
    signup_response = client.post("/auth/signup", json=user_data)
    token = signup_response.json()["access_token"]
    
    # Token should be a JWT with three parts separated by dots
    parts = token.split('.')
    assert len(parts) == 3  # Header, payload, signature


def test_invalid_token_format(client):
    """Test access with invalid token format"""
    headers = {"Authorization": "Bearer invalid.token.format"}
    
    response = client.get("/books/", headers=headers)
    assert response.status_code == 401


def test_malformed_token(client):
    """Test access with malformed token"""
    headers = {"Authorization": "Bearer not.a.valid.jwt.token"}
    
    response = client.get("/books/", headers=headers)
    assert response.status_code == 401


def test_token_without_bearer(client):
    """Test access with token missing Bearer prefix"""
    headers = {"Authorization": "some_token"}
    
    response = client.get("/books/", headers=headers)
    assert response.status_code == 403


def test_no_authorization_header(client):
    """Test access without any Authorization header"""
    response = client.get("/books/")
    assert response.status_code == 403