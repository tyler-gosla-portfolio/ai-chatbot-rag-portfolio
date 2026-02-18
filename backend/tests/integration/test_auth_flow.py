import pytest
from httpx import AsyncClient

class TestAuthFlow:
    @pytest.mark.asyncio
    async def test_register(self, client: AsyncClient):
        response = await client.post("/api/v1/auth/register", json={
            "email": "newuser@example.com",
            "password": "securepass123",
            "display_name": "New User",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["display_name"] == "New User"
        assert data["is_active"] is True

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient):
        # Register first user
        await client.post("/api/v1/auth/register", json={
            "email": "dupe@example.com",
            "password": "securepass123",
        })
        # Try duplicate
        response = await client.post("/api/v1/auth/register", json={
            "email": "dupe@example.com",
            "password": "securepass123",
        })
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient):
        # Register
        await client.post("/api/v1/auth/register", json={
            "email": "login@example.com",
            "password": "securepass123",
        })
        # Login
        response = await client.post("/api/v1/auth/login", json={
            "email": "login@example.com",
            "password": "securepass123",
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient):
        await client.post("/api/v1/auth/register", json={
            "email": "wrongpw@example.com",
            "password": "securepass123",
        })
        response = await client.post("/api/v1/auth/login", json={
            "email": "wrongpw@example.com",
            "password": "wrongpassword",
        })
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_me(self, client: AsyncClient):
        # Register + login
        await client.post("/api/v1/auth/register", json={
            "email": "me@example.com",
            "password": "securepass123",
        })
        login_resp = await client.post("/api/v1/auth/login", json={
            "email": "me@example.com",
            "password": "securepass123",
        })
        token = login_resp.json()["access_token"]

        # Get me
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert response.json()["email"] == "me@example.com"

    @pytest.mark.asyncio
    async def test_get_me_unauthorized(self, client: AsyncClient):
        response = await client.get("/api/v1/auth/me")
        assert response.status_code in [401, 403]
