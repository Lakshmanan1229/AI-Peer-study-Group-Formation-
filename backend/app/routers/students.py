from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.security import get_current_student
from app.models.student import Student
from app.schemas.student import (
    AvailabilityBulkUpdate,
    GoalUpdate,
    SkillBulkUpdate,
    SkillResponse,
    StudentProfile,
    StudentProfileUpdate,
)
from app.services import student_service

router = APIRouter(prefix="/students", tags=["Students"])


@router.get("/me", response_model=StudentProfile)
async def get_me(
    current_student: Student = Depends(get_current_student),
) -> Student:
    """Return the authenticated student's profile."""
    return current_student


@router.put("/me", response_model=StudentProfile)
async def update_me(
    update_data: StudentProfileUpdate,
    current_student: Student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db),
) -> Student:
    """Partially update the authenticated student's profile fields."""
    return await student_service.update_profile(db, current_student.id, update_data)


@router.put("/me/skills", response_model=List[SkillResponse])
async def update_skills(
    body: SkillBulkUpdate,
    current_student: Student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db),
) -> list:
    """Bulk-upsert skill self-assessments for the authenticated student."""
    return await student_service.update_skills(db, current_student.id, body.skills)


@router.get("/me/skills", response_model=List[SkillResponse])
async def get_skills(
    current_student: Student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db),
) -> list:
    """Return all skill assessments for the authenticated student."""
    return await student_service.get_skills(db, current_student.id)


@router.put("/me/schedule", response_model=List[dict])
async def update_schedule(
    body: AvailabilityBulkUpdate,
    current_student: Student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db),
) -> list:
    """Bulk-upsert availability slots for the authenticated student."""
    slots = await student_service.update_schedule(
        db, current_student.id, body.slots
    )
    return [
        {
            "day_of_week": s.day_of_week,
            "slot": s.slot.value if hasattr(s.slot, "value") else s.slot,
            "is_available": s.is_available,
        }
        for s in slots
    ]


@router.put("/me/goals", response_model=StudentProfile)
async def update_goals(
    body: GoalUpdate,
    current_student: Student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db),
) -> Student:
    """Update the student's study goals and regenerate the goal embedding."""
    return await student_service.update_goals(db, current_student.id, body.goals)

