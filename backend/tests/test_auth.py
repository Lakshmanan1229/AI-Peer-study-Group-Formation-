from __future__ import annotations

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_register_success(test_client: AsyncClient, sample_student_data: dict):
    """POST /v1/auth/register with valid data returns 201 and an access_token."""
    resp = await test_client.post("/v1/auth/register", json=sample_student_data)
    assert resp.status_code == 201
    body = resp.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"


async def test_register_duplicate_email(
    test_client: AsyncClient, sample_student_data: dict
):
    """Registering the same email twice returns 400."""
    await test_client.post("/v1/auth/register", json=sample_student_data)
    resp = await test_client.post("/v1/auth/register", json=sample_student_data)
    assert resp.status_code == 400


async def test_login_success(test_client: AsyncClient, sample_student_data: dict):
    """Login with correct credentials returns 200 and an access_token."""
    await test_client.post("/v1/auth/register", json=sample_student_data)
    resp = await test_client.post(
        "/v1/auth/login",
        json={
            "email": sample_student_data["email"],
            "password": sample_student_data["password"],
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body


async def test_login_wrong_password(
    test_client: AsyncClient, sample_student_data: dict
):
    """Login with wrong password returns 401."""
    await test_client.post("/v1/auth/register", json=sample_student_data)
    resp = await test_client.post(
        "/v1/auth/login",
        json={"email": sample_student_data["email"], "password": "WrongPass999"},
    )
    assert resp.status_code == 401


async def test_login_nonexistent_user(test_client: AsyncClient):
    """Login with a non-existent email returns 401."""
    resp = await test_client.post(
        "/v1/auth/login",
        json={"email": "nobody@nowhere.com", "password": "SomePass123"},
    )
    assert resp.status_code == 401


async def test_refresh_token(test_client: AsyncClient, sample_student_data: dict):
    """A valid refresh token produces a new access_token."""
    reg = await test_client.post("/v1/auth/register", json=sample_student_data)
    refresh_token = reg.json()["refresh_token"]

    resp = await test_client.post(
        "/v1/auth/refresh", json={"refresh_token": refresh_token}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert "refresh_token" in body
