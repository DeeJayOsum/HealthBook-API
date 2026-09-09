import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_login_and_read_current_user(client: AsyncClient):
    registration = await client.post(
        "/api/v1/auth/register",
        json={"email": "patient@example.com", "password": "strong-password"},
    )
    assert registration.status_code == 201
    assert registration.json()["role"] == "patient"

    login = await client.post(
        "/api/v1/auth/login",
        data={"username": "patient@example.com", "password": "strong-password"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]

    current_user = await client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert current_user.status_code == 200
    assert current_user.json()["email"] == "patient@example.com"

    refresh = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": login.json()["refresh_token"]}
    )
    assert refresh.status_code == 200
    assert refresh.json()["access_token"]


@pytest.mark.asyncio
async def test_me_requires_authentication(client: AsyncClient):
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_register_validates_password_length(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "patient@example.com", "password": "short"},
    )
    assert response.status_code == 422