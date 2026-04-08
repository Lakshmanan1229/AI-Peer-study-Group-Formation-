from __future__ import annotations

import uuid
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.security import get_current_student
from app.models.group import GroupMembership, GroupSession, SessionTypeEnum, StudyGroup
from app.models.student import Student
from app.schemas.group import GroupDetail, GroupHealthResponse, SessionCreate, SkillExchangeItem
from app.services import group_service, recommendation_service

router = APIRouter(prefix="/groups", tags=["Groups"])


@router.get("/my-group", response_model=GroupDetail)
async def get_my_group(
    current_student: Student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db),
) -> GroupDetail:
    """Return the current student's active study group with full member details."""
    group_detail = await group_service.get_student_group(db, current_student.id)
    if group_detail is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not currently assigned to a study group.",
        )
    return group_detail


@router.get("/my-group/health", response_model=GroupHealthResponse)
async def get_my_group_health(
    current_student: Student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db),
) -> GroupHealthResponse:
    """Return the health score and factor breakdown for the student's group."""
    # Resolve the group id first
    result = await db.execute(
        select(GroupMembership).where(
            GroupMembership.student_id == current_student.id,
            GroupMembership.left_at.is_(None),
        )
    )
    membership = result.scalar_one_or_none()
    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not currently assigned to a study group.",
        )
    return await group_service.calculate_health_score(db, membership.group_id)


@router.post("/my-group/sessions", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_session(
    body: SessionCreate,
    current_student: Student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Create a new study session for the current student's group."""
    result = await db.execute(
        select(GroupMembership).where(
            GroupMembership.student_id == current_student.id,
            GroupMembership.left_at.is_(None),
        )
    )
    membership = result.scalar_one_or_none()
    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not currently assigned to a study group.",
        )

    session = GroupSession(
        group_id=membership.group_id,
        scheduled_at=body.scheduled_at,
        duration_minutes=body.duration_minutes,
        location=body.location,
        session_type=SessionTypeEnum(body.session_type),
        notes=body.notes,
        created_by=current_student.id,
        attendance={},
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    return {
        "id": str(session.id),
        "group_id": str(session.group_id),
        "scheduled_at": session.scheduled_at.isoformat(),
        "duration_minutes": session.duration_minutes,
        "location": session.location,
        "session_type": session.session_type.value,
        "notes": session.notes,
        "created_at": session.created_at.isoformat(),
    }


@router.get("/my-group/skill-exchange", response_model=List[SkillExchangeItem])
async def get_skill_exchange(
    current_student: Student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db),
) -> List[SkillExchangeItem]:
    """Return a skill-exchange map showing peer-teaching opportunities."""
    result = await db.execute(
        select(GroupMembership).where(
            GroupMembership.student_id == current_student.id,
            GroupMembership.left_at.is_(None),
        )
    )
    membership = result.scalar_one_or_none()
    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not currently assigned to a study group.",
        )

    from sqlalchemy.orm import selectinload

    group_result = await db.execute(
        select(StudyGroup)
        .where(StudyGroup.id == membership.group_id)
        .options(
            selectinload(StudyGroup.memberships)
            .selectinload(GroupMembership.student)
            .selectinload(Student.skills),
        )
    )
    group = group_result.scalar_one()
    active_members = [m.student for m in group.memberships if m.left_at is None]
    return group_service.build_skill_exchange_map(active_members)


@router.get("/my-group/resources", response_model=List[Dict[str, Any]])
async def get_group_resources(
    current_student: Student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db),
) -> List[Dict[str, Any]]:
    """Return AI-recommended learning resources aggregated for the group's weak areas."""
    return await recommendation_service.get_resource_recommendations(
        db, current_student.id
    )

