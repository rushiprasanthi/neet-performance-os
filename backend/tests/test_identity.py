"""Tests for Identity domain."""

import pytest

from app.domains.identity.services.auth_service import AuthService


@pytest.mark.asyncio
async def test_user_registration_success(client):
    """Test successful user registration."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "student@neet.com",
            "password": "SecurePassword123!",
            "first_name": "John",
            "last_name": "Doe",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["user"]["email"] == "student@neet.com"
    assert data["user"]["status"] == "pending"
    assert data["user"]["email_verified"] is False
    assert data["user"]["profile"] is None
    assert "Registration successful" in data["message"]


@pytest.mark.asyncio
async def test_user_registration_duplicate_email(client):
    """Test registration with duplicate email."""
    # First registration
    response1 = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "duplicate@neet.com",
            "password": "SecurePassword123!",
            "first_name": "Jane",
            "last_name": "Smith",
        },
    )
    assert response1.status_code == 201

    # Duplicate registration
    response2 = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "duplicate@neet.com",
            "password": "DifferentPassword456!",
            "first_name": "Jane",
            "last_name": "Smith",
        },
    )
    assert response2.status_code == 409
    assert "already exists" in response2.json()["detail"].lower()


@pytest.mark.asyncio
async def test_user_registration_invalid_email(client):
    """Test registration with invalid email."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "invalid-email",
            "password": "SecurePassword123!",
        },
    )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_registration_normalizes_email_case(client):
    """Test that duplicate registration is treated consistently regardless of email case."""
    first_response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "CaseUser@Neet.com",
            "password": "SecurePassword123!",
            "first_name": "Case",
            "last_name": "User",
        },
    )
    assert first_response.status_code == 201

    duplicate_response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "caseuser@neet.com",
            "password": "DifferentPassword456!",
            "first_name": "Case",
            "last_name": "User",
        },
    )

    assert duplicate_response.status_code == 409
    assert "already exists" in duplicate_response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_user_registration_weak_password(client):
    """Test registration with weak password."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "student@neet.com",
            "password": "weak",
        },
    )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_password_hashing():
    """Test password hashing with Argon2id."""
    plain_password = "SecurePassword123!"
    
    # Hash password
    hashed = AuthService.hash_password(plain_password)
    
    # Verify it's different from plain
    assert hashed != plain_password
    
    # Verify correct password
    assert AuthService.verify_password(plain_password, hashed) is True
    
    # Verify wrong password
    assert AuthService.verify_password("WrongPassword456!", hashed) is False


@pytest.mark.asyncio
async def test_identity_health_check(client):
    """Test identity domain health endpoint."""
    response = await client.get("/api/v1/auth/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["domain"] == "identity"