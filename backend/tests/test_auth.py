import pytest


@pytest.mark.asyncio
async def test_register_login_refresh(client):
    payload = {"email": "auth@example.com", "password": "password123"}

    register = await client.post("/api/v1/auth/register", json=payload)
    assert register.status_code == 201
    assert register.json()["user"]["email"] == payload["email"]

    login = await client.post("/api/v1/auth/login", json=payload)
    assert login.status_code == 200
    assert login.json()["tokens"]["access_token"]

    refresh = await client.post("/api/v1/auth/refresh", cookies=login.cookies)
    assert refresh.status_code == 200
    assert refresh.json()["access_token"]
