from __future__ import annotations

import uuid
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.security import get_current_student
from app.models.feedback import PeerFeedback
from app.models.group import GroupMembership, GroupSession
from app.models.student import Student
from app.schemas.feedback import FeedbackBulkSubmit, GroupReportResponse

router = APIRouter(prefix="/feedback", tags=["Feedback"])


@router.post("/submit", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    body: FeedbackBulkSubmit,
    current_student: Student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Submit peer feedback for one or more group members.

    The reviewer must be in an active group.  Each ``reviewee_id`` must also
    be a member of the same group.
    """
    # Resolve reviewer's active group
    result = await db.execute(
        select(GroupMembership).where(
            GroupMembership.student_id == current_student.id,
            GroupMembership.left_at.is_(None),
        )
    )
    membership = result.scalar_one_or_none()
    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must be assigned to a group before submitting feedback.",
        )

    group_id = membership.group_id

    # Validate reviewees are in the same group
    members_result = await db.execute(
        select(GroupMembership.student_id).where(
            GroupMembership.group_id == group_id,
            GroupMembership.left_at.is_(None),
        )
    )
    member_ids: set[uuid.UUID] = {row for (row,) in members_result.all()}

    created_ids: List[str] = []
    for fb_input in body.feedbacks:
        if fb_input.reviewee_id not in member_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Reviewee {fb_input.reviewee_id} is not in your group.",
            )
        if fb_input.reviewee_id == current_student.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot submit feedback for yourself.",
            )

        feedback = PeerFeedback(
            reviewer_id=current_student.id,
            reviewee_id=fb_input.reviewee_id,
            group_id=group_id,
            session_id=body.session_id,
            rating=fb_input.rating,
            helpfulness_score=fb_input.helpfulness_score,
            comment=fb_input.comment or "",
            is_anonymous=fb_input.is_anonymous,
        )
        db.add(feedback)
        await db.flush()
        created_ids.append(str(feedback.id))

    await db.commit()
    return {"submitted": len(created_ids), "feedback_ids": created_ids}


@router.get("/group-report", response_model=GroupReportResponse)
async def get_group_report(
    current_student: Student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db),
) -> GroupReportResponse:
    """Return an aggregated feedback report for the student's group."""
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

    group_id = membership.group_id

    # Overall averages
    avg_result = await db.execute(
        select(
            func.avg(PeerFeedback.rating),
            func.avg(PeerFeedback.helpfulness_score),
        ).where(PeerFeedback.group_id == group_id)
    )
    avg_rating, avg_helpfulness = avg_result.one()

    # Per-member reports
    members_result = await db.execute(
        select(GroupMembership).where(
            GroupMembership.group_id == group_id,
            GroupMembership.left_at.is_(None),
        )
    )
    memberships = members_result.scalars().all()

    member_reports: List[Dict[str, Any]] = []
    for m in memberships:
        m_avg = await db.execute(
            select(
                func.avg(PeerFeedback.rating),
                func.avg(PeerFeedback.helpfulness_score),
                func.count(PeerFeedback.id),
            ).where(
                PeerFeedback.group_id == group_id,
                PeerFeedback.reviewee_id == m.student_id,
            )
        )
        m_rating, m_helpfulness, m_count = m_avg.one()
        member_reports.append(
            {
                "student_id": str(m.student_id),
                "avg_rating": round(float(m_rating), 2) if m_rating else None,
                "avg_helpfulness": round(float(m_helpfulness), 2) if m_helpfulness else None,
                "feedback_count": m_count or 0,
            }
        )

    # Total sessions
    sessions_result = await db.execute(
        select(func.count(GroupSession.id)).where(
            GroupSession.group_id == group_id
        )
    )
    total_sessions = sessions_result.scalar_one() or 0

    return GroupReportResponse(
        group_id=group_id,
        avg_rating=round(float(avg_rating), 2) if avg_rating else 0.0,
        avg_helpfulness=round(float(avg_helpfulness), 2) if avg_helpfulness else 0.0,
        member_reports=member_reports,
        total_sessions=total_sessions,
    )

