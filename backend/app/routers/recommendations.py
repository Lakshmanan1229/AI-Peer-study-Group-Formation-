from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.security import get_current_student
from app.models.student import Student
from app.services import recommendation_service

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("/resources", response_model=List[Dict[str, Any]])
async def get_resource_recommendations(
    current_student: Student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db),
) -> List[Dict[str, Any]]:
    """Return AI-curated study resources ranked by relevance to weak subjects."""
    return await recommendation_service.get_resource_recommendations(
        db, current_student.id
    )


@router.get("/mentors", response_model=List[Dict[str, Any]])
async def get_mentor_recommendations(
    current_student: Student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db),
) -> List[Dict[str, Any]]:
    """Return senior students who are strong in the current student's weak subjects."""
    return await recommendation_service.get_mentor_recommendations(
        db, current_student.id
    )

