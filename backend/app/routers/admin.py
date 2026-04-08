from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.security import require_admin
from app.models.group import GroupMembership, GroupStatusEnum, StudyGroup
from app.models.student import Student
from app.schemas.student import StudentProfile
from app.services import group_service

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/trigger-grouping", response_model=Dict[str, Any])
async def trigger_grouping(
    _admin: Student = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Run the full AI group-formation pipeline and return summary statistics."""
    stats = await group_service.run_group_formation_pipeline(db)
    return {"status": "completed", **stats}


@router.get("/analytics/dashboard", response_model=Dict[str, Any])
async def analytics_dashboard(
    _admin: Student = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Return system-wide statistics for the admin dashboard."""
    total_students = (
        await db.execute(select(func.count(Student.id)))
    ).scalar_one() or 0

    active_students = (
        await db.execute(
            select(func.count(Student.id)).where(Student.is_active)
        )
    ).scalar_one() or 0

    total_groups = (
        await db.execute(select(func.count(StudyGroup.id)))
    ).scalar_one() or 0

    active_groups = (
        await db.execute(
            select(func.count(StudyGroup.id)).where(
                StudyGroup.status == GroupStatusEnum.active
            )
        )
    ).scalar_one() or 0

    avg_group_size_row = await db.execute(
        select(func.avg(func.count(GroupMembership.student_id)))
        .where(GroupMembership.left_at.is_(None))
        .group_by(GroupMembership.group_id)
    )
    avg_group_size = avg_group_size_row.scalar_one_or_none()

    return {
        "total_students": total_students,
        "active_students": active_students,
        "total_groups": total_groups,
        "active_groups": active_groups,
        "avg_group_size": round(float(avg_group_size), 2) if avg_group_size else 0.0,
    }


@router.get("/students", response_model=Dict[str, Any])
async def list_students(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    _admin: Student = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Return a paginated list of all registered students."""
    offset = (page - 1) * page_size

    total = (
        await db.execute(select(func.count(Student.id)))
    ).scalar_one() or 0

    students_result = await db.execute(
        select(Student).order_by(Student.created_at.desc()).offset(offset).limit(page_size)
    )
    students = students_result.scalars().all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size,
        "items": [
            {
                "id": str(s.id),
                "email": s.email,
                "full_name": s.full_name,
                "department": (
                    s.department.value if hasattr(s.department, "value") else str(s.department)
                ),
                "year": s.year,
                "cgpa": s.cgpa,
                "role": (
                    s.role.value if hasattr(s.role, "value") else str(s.role)
                ),
                "is_active": s.is_active,
                "created_at": s.created_at.isoformat(),
            }
            for s in students
        ],
    }


@router.get("/groups", response_model=Dict[str, Any])
async def list_groups(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    _admin: Student = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Return a paginated list of all study groups with member counts."""
    offset = (page - 1) * page_size

    total = (
        await db.execute(select(func.count(StudyGroup.id)))
    ).scalar_one() or 0

    groups_result = await db.execute(
        select(StudyGroup)
        .order_by(StudyGroup.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    groups = groups_result.scalars().all()

    # Fetch member counts in one query
    member_count_rows = await db.execute(
        select(GroupMembership.group_id, func.count(GroupMembership.id))
        .where(GroupMembership.left_at.is_(None))
        .group_by(GroupMembership.group_id)
    )
    member_counts: Dict[str, int] = {
        str(gid): cnt for gid, cnt in member_count_rows.all()
    }

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size,
        "items": [
            {
                "id": str(g.id),
                "name": g.name,
                "department": g.department,
                "status": (
                    g.status.value if hasattr(g.status, "value") else str(g.status)
                ),
                "member_count": member_counts.get(str(g.id), 0),
                "complementary_score": g.complementary_score,
                "schedule_overlap_count": g.schedule_overlap_count,
                "goal_similarity_score": g.goal_similarity_score,
                "created_at": g.created_at.isoformat(),
            }
            for g in groups
        ],
    }

