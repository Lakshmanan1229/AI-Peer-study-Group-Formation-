from __future__ import annotations

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_get_profile(test_client: AsyncClient, auth_headers: dict, sample_student_data: dict):
    """GET /v1/students/me with valid auth returns 200 and the correct email."""
    resp = await test_client.get("/v1/students/me", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == sample_student_data["email"]
    assert body["full_name"] == sample_student_data["full_name"]


async def test_get_profile_unauthorized(test_client: AsyncClient):
    """GET /v1/students/me without auth returns 401."""
    resp = await test_client.get("/v1/students/me")
    assert resp.status_code == 401


async def test_update_profile(test_client: AsyncClient, auth_headers: dict):
    """PUT /v1/students/me updates profile fields and returns 200."""
    update_payload = {"full_name": "Updated Name", "cgpa": 9.1, "year": 3}
    resp = await test_client.put(
        "/v1/students/me", json=update_payload, headers=auth_headers
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["full_name"] == "Updated Name"
    assert body["cgpa"] == pytest.approx(9.1, abs=0.01)
    assert body["year"] == 3


async def test_update_skills(test_client: AsyncClient, auth_headers: dict):
    """PUT /v1/students/me/skills with a list of skills returns 200."""
    skills_payload = {
        "skills": [
            {"subject": "DSA", "self_rating": 8, "grade_points": 9.0},
            {"subject": "OOP", "self_rating": 7, "grade_points": 8.5},
        ]
    }
    resp = await test_client.put(
        "/v1/students/me/skills", json=skills_payload, headers=auth_headers
    )
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    assert len(body) == 2
    subjects = {s["subject"] for s in body}
    assert subjects == {"DSA", "OOP"}


async def test_get_skills(test_client: AsyncClient, auth_headers: dict):
    """GET /v1/students/me/skills returns 200 with a list of skills."""
    # Add skills first
    skills_payload = {
        "skills": [{"subject": "ML", "self_rating": 6, "grade_points": 7.5}]
    }
    await test_client.put(
        "/v1/students/me/skills", json=skills_payload, headers=auth_headers
    )

    resp = await test_client.get("/v1/students/me/skills", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    assert any(s["subject"] == "ML" for s in body)


async def test_update_schedule(test_client: AsyncClient, auth_headers: dict):
    """PUT /v1/students/me/schedule returns 200 with updated slots."""
    schedule_payload = {
        "slots": [
            {"day_of_week": 0, "slot": "morning", "is_available": True},
            {"day_of_week": 1, "slot": "evening", "is_available": True},
        ]
    }
    resp = await test_client.put(
        "/v1/students/me/schedule", json=schedule_payload, headers=auth_headers
    )
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    available = [s for s in body if s["is_available"]]
    assert len(available) >= 2


async def test_update_goals(test_client: AsyncClient, auth_headers: dict):
    """PUT /v1/students/me/goals returns 200."""
    goals_payload = {"goals": "I want to master data structures and algorithms."}
    resp = await test_client.put(
        "/v1/students/me/goals", json=goals_payload, headers=auth_headers
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "id" in body
