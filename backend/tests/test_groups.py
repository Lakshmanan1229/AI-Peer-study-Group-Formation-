from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


# ---------------------------------------------------------------------------
# Helper fixture: register students, add skills/availability, trigger grouping
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture(scope="function")
async def grouped_students(test_client: AsyncClient, admin_headers: dict):
    """Register multiple students with skills and availability, then trigger grouping."""
    student_headers = []

    departments = ["CSE", "CSE", "IT", "IT", "ECE"]
    for i in range(5):
        reg_data = {
            "email": f"groupstudent{i}@example.com",
            "password": "SecurePass123",
            "full_name": f"Group Student {i}",
            "department": departments[i],
            "year": (i % 4) + 1,
            "cgpa": 7.0 + i * 0.5,
            "learning_pace": ["slow", "moderate", "fast"][i % 3],
        }
        resp = await test_client.post("/v1/auth/register", json=reg_data)
        assert resp.status_code in (200, 201), (
            f"Registration failed for student {i}: {resp.text}"
        )
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        student_headers.append(headers)

        # Add skills
        skills_payload = {
            "skills": [
                {"subject": "DSA", "self_rating": (i + 3) % 10 + 1, "grade_points": 7.0},
                {"subject": "OOP", "self_rating": (i + 5) % 10 + 1, "grade_points": 8.0},
                {"subject": "DBMS", "self_rating": (i + 2) % 10 + 1, "grade_points": 6.5},
            ]
        }
        await test_client.put(
            "/v1/students/me/skills", json=skills_payload, headers=headers
        )

        # Add availability
        schedule_payload = {
            "slots": [
                {"day_of_week": 0, "slot": "morning", "is_available": True},
                {"day_of_week": 1, "slot": "afternoon", "is_available": True},
                {"day_of_week": 2, "slot": "evening", "is_available": True},
            ]
        }
        await test_client.put(
            "/v1/students/me/schedule", json=schedule_payload, headers=headers
        )

    # Trigger grouping
    resp = await test_client.post("/v1/admin/trigger-grouping", headers=admin_headers)
    assert resp.status_code == 200, f"Grouping failed: {resp.text}"

    return student_headers


# ---------------------------------------------------------------------------
# 1-3: No-group 404 tests (original tests preserved)
# ---------------------------------------------------------------------------


async def test_get_group_no_group(test_client: AsyncClient, auth_headers: dict):
    """GET /v1/groups/my-group when no group exists returns 404."""
    resp = await test_client.get("/v1/groups/my-group", headers=auth_headers)
    assert resp.status_code == 404


async def test_get_group_health_no_group(test_client: AsyncClient, auth_headers: dict):
    """GET /v1/groups/my-group/health returns 404 when student has no group."""
    resp = await test_client.get("/v1/groups/my-group/health", headers=auth_headers)
    assert resp.status_code == 404


async def test_create_session_no_group(test_client: AsyncClient, auth_headers: dict):
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


# ---------------------------------------------------------------------------
# 4: Skill-exchange no-group 404
# ---------------------------------------------------------------------------


async def test_skill_exchange_no_group(test_client: AsyncClient, auth_headers: dict):
    """GET /v1/groups/my-group/skill-exchange returns 404 when no group."""
    resp = await test_client.get(
        "/v1/groups/my-group/skill-exchange", headers=auth_headers
    )
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# 5-6: Admin grouping endpoint
# ---------------------------------------------------------------------------


async def test_trigger_grouping_requires_admin(
    test_client: AsyncClient, auth_headers: dict
):
    """POST /v1/admin/trigger-grouping with regular auth returns 403."""
    resp = await test_client.post(
        "/v1/admin/trigger-grouping", headers=auth_headers
    )
    assert resp.status_code == 403


async def test_trigger_grouping_as_admin(
    test_client: AsyncClient, admin_headers: dict
):
    """POST /v1/admin/trigger-grouping with admin_headers succeeds."""
    resp = await test_client.post(
        "/v1/admin/trigger-grouping", headers=admin_headers
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "groups_formed" in body


# ---------------------------------------------------------------------------
# 7-10: Tests after grouping (require grouped_students fixture)
# ---------------------------------------------------------------------------


async def test_get_group_after_grouping(
    test_client: AsyncClient, grouped_students: list[dict]
):
    """After forming groups, GET /v1/groups/my-group should return 200."""
    resp = await test_client.get(
        "/v1/groups/my-group", headers=grouped_students[0]
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "id" in body
    assert "members" in body
    assert len(body["members"]) >= 1


async def test_health_score_after_grouping(
    test_client: AsyncClient, grouped_students: list[dict]
):
    """After forming groups, GET health returns 200 with health_score."""
    resp = await test_client.get(
        "/v1/groups/my-group/health", headers=grouped_students[0]
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "health_score" in body
    assert isinstance(body["health_score"], (int, float))


async def test_skill_exchange_after_grouping(
    test_client: AsyncClient, grouped_students: list[dict]
):
    """After forming groups, GET skill-exchange returns 200."""
    resp = await test_client.get(
        "/v1/groups/my-group/skill-exchange", headers=grouped_students[0]
    )
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)


async def test_create_session_after_grouping(
    test_client: AsyncClient, grouped_students: list[dict]
):
    """After forming groups, creating a session returns 200 or 201."""
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
        headers=grouped_students[0],
    )
    assert resp.status_code in (200, 201)
    body = resp.json()
    assert "id" in body
    assert "group_id" in body


# ---------------------------------------------------------------------------
# 11-12: Unauthorized access tests
# ---------------------------------------------------------------------------


async def test_get_group_unauthorized(test_client: AsyncClient):
    """GET /v1/groups/my-group without auth returns 401."""
    resp = await test_client.get("/v1/groups/my-group")
    assert resp.status_code == 401


async def test_health_unauthorized(test_client: AsyncClient):
    """GET /v1/groups/my-group/health without auth returns 401."""
    resp = await test_client.get("/v1/groups/my-group/health")
    assert resp.status_code == 401
