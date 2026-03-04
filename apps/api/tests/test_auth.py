"""
Minimal auth API tests: register, login, refresh.
Requires DB running and migrated: cd apps/api && alembic upgrade head
"""
import uuid

import pytest


@pytest.mark.asyncio
async def test_register(client):
    """POST /api/auth/register creates a user and returns user + sets cookies."""
    email = f"test-{uuid.uuid4().hex[:8]}@example.com"
    r = await client.post(
        "/api/auth/register",
        json={"email": email, "password": "SecurePass123!"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["email"] == email
    assert "id" in data
    assert data.get("is_verified") is False


@pytest.mark.asyncio
async def test_login(client):
    """POST /api/auth/login with valid credentials returns tokens and sets cookies."""
    email = f"test-{uuid.uuid4().hex[:8]}@example.com"
    password = "SecurePass123!"
    await client.post("/api/auth/register", json={"email": email, "password": password})
    r = await client.post("/api/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data.get("token_type") == "Bearer"
    assert "refresh_token" in r.cookies or "access_token" in r.cookies


@pytest.mark.asyncio
async def test_refresh(client):
    """POST /api/auth/refresh with refresh cookie returns new tokens."""
    email = f"test-{uuid.uuid4().hex[:8]}@example.com"
    password = "SecurePass123!"
    await client.post("/api/auth/register", json={"email": email, "password": password})
    await client.post("/api/auth/login", json={"email": email, "password": password})
    r = await client.post("/api/auth/refresh")
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data
    assert "refresh_token" in data
