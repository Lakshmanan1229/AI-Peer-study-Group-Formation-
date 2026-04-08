from __future__ import annotations

import logging
import uuid
from typing import List

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.student import AvailabilitySlot, SkillAssessment, SlotEnum, Student
from app.schemas.student import AvailabilityInput, SkillInput, StudentProfileUpdate

logger = logging.getLogger(__name__)


async def get_profile(db: AsyncSession, student_id: uuid.UUID) -> Student:
    """Fetch a student by primary key.

    Raises:
        HTTPException 404: if the student is not found.
    """
    result = await db.execute(select(Student).where(Student.id == student_id))
    student = result.scalar_one_or_none()
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found.",
        )
    return student


async def update_profile(
    db: AsyncSession,
    student_id: uuid.UUID,
    update_data: StudentProfileUpdate,
) -> Student:
    """Apply a partial update to a student's profile fields."""
    student = await get_profile(db, student_id)
    for field, value in update_data.model_dump(exclude_none=True).items():
        setattr(student, field, value)
    await db.commit()
    await db.refresh(student)
    return student


async def update_skills(
    db: AsyncSession,
    student_id: uuid.UUID,
    skills: List[SkillInput],
) -> List[SkillAssessment]:
    """Upsert skill assessments for a student.

    Existing records for the same subject are updated in-place; new subjects
    create fresh ``SkillAssessment`` rows.
    """
    result = await db.execute(
        select(SkillAssessment).where(SkillAssessment.student_id == student_id)
    )
    existing: dict[str, SkillAssessment] = {
        s.subject: s for s in result.scalars().all()
    }

    updated: List[SkillAssessment] = []
    for item in skills:
        if item.subject in existing:
            record = existing[item.subject]
            record.self_rating = item.self_rating
            if item.grade_points is not None:
                record.grade_points = item.grade_points
        else:
            record = SkillAssessment(
                student_id=student_id,
                subject=item.subject,
                self_rating=item.self_rating,
                grade_points=item.grade_points,
            )
            db.add(record)
        updated.append(record)

    await db.commit()
    for record in updated:
        await db.refresh(record)
    return updated


async def get_skills(
    db: AsyncSession,
    student_id: uuid.UUID,
) -> List[SkillAssessment]:
    """Return all skill assessments for a student."""
    result = await db.execute(
        select(SkillAssessment).where(SkillAssessment.student_id == student_id)
    )
    return list(result.scalars().all())


async def update_schedule(
    db: AsyncSession,
    student_id: uuid.UUID,
    slots: List[AvailabilityInput],
) -> List[AvailabilitySlot]:
    """Upsert availability slots for a student.

    Existing (day, slot) pairs are updated; missing pairs are created.
    """
    result = await db.execute(
        select(AvailabilitySlot).where(AvailabilitySlot.student_id == student_id)
    )
    existing: dict[tuple[int, str], AvailabilitySlot] = {
        (s.day_of_week, s.slot.value): s for s in result.scalars().all()
    }

    updated: List[AvailabilitySlot] = []
    for item in slots:
        key = (item.day_of_week, item.slot)
        if key in existing:
            record = existing[key]
            record.is_available = item.is_available
        else:
            record = AvailabilitySlot(
                student_id=student_id,
                day_of_week=item.day_of_week,
                slot=SlotEnum(item.slot),
                is_available=item.is_available,
            )
            db.add(record)
        updated.append(record)

    await db.commit()
    for record in updated:
        await db.refresh(record)
    return updated


async def update_goals(
    db: AsyncSession,
    student_id: uuid.UUID,
    goals_text: str,
) -> Student:
    """Update the student's goals and regenerate the goal embedding.

    Embedding generation is non-fatal: if the sentence-transformer model is
    unavailable the goals text is still saved.
    """
    student = await get_profile(db, student_id)
    student.goals = goals_text

    try:
        from app.ml.nlp_goals import generate_goal_embedding

        student.goal_embedding = generate_goal_embedding(goals_text)
    except (ImportError, RuntimeError, OSError) as exc:
        logger.warning(
            "Goal embedding generation failed for student %s (%s); skipping.",
            student_id,
            exc,
        )

    await db.commit()
    await db.refresh(student)
    return student
