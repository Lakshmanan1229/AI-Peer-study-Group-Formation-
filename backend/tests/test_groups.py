from __future__ import annotations

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_get_group_no_group(test_client: AsyncClient, auth_headers: dict):
    """GET /v1/groups/my-group when no group exists returns 404."""
    resp = await test_client.get("/v1/groups/my-group", headers=auth_headers)
    assert resp.status_code == 404


async def test_get_group_health(test_client: AsyncClient, auth_headers: dict):
    """GET /v1/groups/my-group/health returns 404 when student has no group."""
    resp = await test_client.get("/v1/groups/my-group/health", headers=auth_headers)
    assert resp.status_code == 404


async def test_create_session(test_client: AsyncClient, auth_headers: dict):
    """POST /v1/groups/my-group/sessions returns 404 when no group assigned."""
    session_payload = {
        "scheduled_at": "2025-09-01T10:00:00Z",
        "duration_minutes": 60,
        "location": "Library Room 3",
        "session_type": "offline",
        "notes": "First study session",
    }
    resp = await test_client.post(
        "/v1/groups/my-group/sessions",
        json=session_payload,
        headers=auth_headers,
    )
    assert resp.status_code == 404
