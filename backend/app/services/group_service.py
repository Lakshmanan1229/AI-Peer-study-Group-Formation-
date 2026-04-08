from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, List, Optional

from fastapi import HTTPException, status
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.feedback import PeerFeedback
from app.models.group import (
    GroupMembership,
    GroupStatusEnum,
    MemberRoleEnum,
    StudyGroup,
)
from app.models.student import Student
from app.schemas.group import (
    GroupDetail,
    GroupHealthResponse,
    GroupMemberInfo,
    SkillExchangeItem,
)

logger = logging.getLogger(__name__)

_DAY_NAMES = [
    "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday",
]
_SLOT_LABELS = {"morning": "Morning", "afternoon": "Afternoon", "evening": "Evening"}


# ---------------------------------------------------------------------------
# Group formation pipeline
# ---------------------------------------------------------------------------


async def run_group_formation_pipeline(db: AsyncSession) -> Dict[str, Any]:
    """Run the full AI-powered group formation pipeline.

    Steps:
        1. Load all active students (with skills + availability).
        2. Build a numeric feature matrix via ``feature_engineering``.
        3. Cluster students via K-Means.
        4. Optimise group composition via ``group_optimizer``.
        5. Clear existing active memberships/groups.
        6. Persist new ``StudyGroup`` and ``GroupMembership`` records.

    Returns:
        Dict with keys ``groups_formed``, ``students_placed``,
        ``ungrouped_count``.
    """
    from app.ml.clustering import cluster_students
    from app.ml.feature_engineering import build_feature_matrix
    from app.ml.group_optimizer import form_groups

    # 1. Load students
    result = await db.execute(
        select(Student)
        .where(Student.is_active)
        .options(
            selectinload(Student.skills),
            selectinload(Student.availability_slots),
        )
    )
    students: List[Student] = list(result.scalars().all())

    if not students:
        return {"groups_formed": 0, "students_placed": 0, "ungrouped_count": 0}

    # 2. Build student data dicts for ML pipeline
    students_data: List[Dict[str, Any]] = []
    for student in students:
        skills_list = [
            {
                "subject": skill.subject,
                "self_rating": skill.self_rating,
                "peer_rating": skill.peer_rating,
                "grade_points": skill.grade_points,
            }
            for skill in student.skills
        ]
        avail_list = [
            {
                "day_of_week": slot.day_of_week,
                "slot": slot.slot.value if hasattr(slot.slot, "value") else str(slot.slot),
                "is_available": slot.is_available,
            }
            for slot in student.availability
        ]
        students_data.append(
            {
                "id": str(student.id),
                "student_id": str(student.id),
                "department": (
                    student.department.value
                    if hasattr(student.department, "value")
                    else str(student.department)
                ),
                "year": student.year,
                "cgpa": student.cgpa,
                "learning_pace": (
                    student.learning_pace.value
                    if hasattr(student.learning_pace, "value")
                    else str(student.learning_pace)
                ),
                "skills": skills_list,
                "availability": avail_list,
            }
        )

    # 3 & 4. Feature matrix → cluster → form groups
    feature_matrix, _student_ids, _feature_names = build_feature_matrix(students_data)
    cluster_labels = cluster_students(feature_matrix)
    groups_of_ids: List[List[str]] = form_groups(
        students_data, cluster_labels, feature_matrix
    )

    # 5. Clear existing active groups and memberships
    active_student_ids = [s.id for s in students]
    await db.execute(
        delete(GroupMembership).where(
            GroupMembership.student_id.in_(active_student_ids)
        )
    )
    await db.execute(
        delete(StudyGroup).where(StudyGroup.status == GroupStatusEnum.active)
    )

    # 6. Persist new groups
    student_lookup: Dict[str, Student] = {str(s.id): s for s in students}
    groups_formed = 0
    students_placed = 0

    for idx, group_ids in enumerate(groups_of_ids):
        if not group_ids:
            continue

        # Determine group department by majority vote
        dept_counts: Dict[str, int] = {}
        for sid in group_ids:
            s = student_lookup.get(sid)
            if s:
                dept = (
                    s.department.value
                    if hasattr(s.department, "value")
                    else str(s.department)
                )
                dept_counts[dept] = dept_counts.get(dept, 0) + 1
        group_dept = max(dept_counts, key=lambda k: dept_counts[k], default="CSE")

        group = StudyGroup(
            name=f"Study Group {idx + 1}",
            department=group_dept,
            status=GroupStatusEnum.active,
            max_size=6,
        )
        db.add(group)
        await db.flush()  # populate group.id

        for position, sid in enumerate(group_ids):
            db.add(
                GroupMembership(
                    group_id=group.id,
                    student_id=uuid.UUID(sid),
                    role=MemberRoleEnum.leader if position == 0 else MemberRoleEnum.member,
                )
            )
            students_placed += 1

        groups_formed += 1

    await db.commit()

    return {
        "groups_formed": groups_formed,
        "students_placed": students_placed,
        "ungrouped_count": len(students) - students_placed,
    }


# ---------------------------------------------------------------------------
# Student group detail
# ---------------------------------------------------------------------------


async def get_student_group(
    db: AsyncSession,
    student_id: uuid.UUID,
) -> Optional[GroupDetail]:
    """Return full group details for the student's active group, or None."""
    result = await db.execute(
        select(GroupMembership)
        .where(
            GroupMembership.student_id == student_id,
            GroupMembership.left_at.is_(None),
        )
        .options(
            selectinload(GroupMembership.group)
            .selectinload(StudyGroup.memberships)
            .selectinload(GroupMembership.student)
            .selectinload(Student.skills),
            selectinload(GroupMembership.group)
            .selectinload(StudyGroup.memberships)
            .selectinload(GroupMembership.student)
            .selectinload(Student.availability_slots),
        )
    )
    membership = result.scalar_one_or_none()
    if membership is None:
        return None

    group = membership.group
    active_memberships = [m for m in group.memberships if m.left_at is None]

    members: List[GroupMemberInfo] = []
    for m in active_memberships:
        s = m.student
        sorted_skills = sorted(s.skills or [], key=lambda x: x.self_rating, reverse=True)
        strengths = [sk.subject for sk in sorted_skills[:3]]
        weaknesses = [sk.subject for sk in sorted_skills if sk.self_rating < 5][-3:]

        members.append(
            GroupMemberInfo(
                id=s.id,
                full_name=s.full_name,
                department=(
                    s.department.value
                    if hasattr(s.department, "value")
                    else str(s.department)
                ),
                year=s.year,
                cgpa=s.cgpa,
                learning_pace=(
                    s.learning_pace.value
                    if hasattr(s.learning_pace, "value")
                    else str(s.learning_pace)
                ),
                strengths=strengths,
                weaknesses=weaknesses,
            )
        )

    suggested_times = get_suggested_meeting_times(
        [m.student for m in active_memberships]
    )

    return GroupDetail(
        id=group.id,
        name=group.name,
        department=group.department,
        status=(
            group.status.value if hasattr(group.status, "value") else str(group.status)
        ),
        members=members,
        complementary_score=group.complementary_score,
        schedule_overlap_count=group.schedule_overlap_count,
        goal_similarity_score=group.goal_similarity_score,
        suggested_meeting_times=suggested_times,
    )


# ---------------------------------------------------------------------------
# Group health score
# ---------------------------------------------------------------------------


async def calculate_health_score(
    db: AsyncSession,
    group_id: uuid.UUID,
) -> GroupHealthResponse:
    """Compute a 0–100 health score with factor breakdown and recommendations."""
    import numpy as np

    result = await db.execute(
        select(StudyGroup)
        .where(StudyGroup.id == group_id)
        .options(
            selectinload(StudyGroup.memberships)
            .selectinload(GroupMembership.student)
            .selectinload(Student.skills),
            selectinload(StudyGroup.memberships)
            .selectinload(GroupMembership.student)
            .selectinload(Student.availability_slots),
            selectinload(StudyGroup.sessions),
        )
    )
    group = result.scalar_one_or_none()
    if group is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found.",
        )

    active_members = [m for m in group.memberships if m.left_at is None]
    if not active_members:
        return GroupHealthResponse(
            group_id=group_id,
            health_score=0.0,
            factors={},
            recommendations=["No active members in this group."],
        )

    # --- Factor 1: Skill diversity ---
    all_subjects: set[str] = set()
    for m in active_members:
        for sk in (m.student.skills or []):
            all_subjects.add(sk.subject)

    skill_diversity = 50.0
    if all_subjects and len(active_members) > 1:
        stdevs = []
        for subj in all_subjects:
            ratings = [
                sk.self_rating
                for m in active_members
                for sk in (m.student.skills or [])
                if sk.subject == subj
            ]
            if len(ratings) > 1:
                stdevs.append(float(np.std(ratings)))
        if stdevs:
            # std dev on a 1-10 scale → scale to 0-100 (max useful stdev ~4)
            skill_diversity = min(100.0, float(np.mean(stdevs)) * 25)

    # --- Factor 2: Schedule compatibility ---
    total_slots = 7 * 3
    shared_slots = 0
    for day in range(7):
        for slot_name in ("morning", "afternoon", "evening"):
            available_count = sum(
                1
                for m in active_members
                for avail in (m.student.availability or [])
                if avail.day_of_week == day
                and avail.slot.value == slot_name
                and avail.is_available
            )
            if available_count >= 2:
                shared_slots += 1
    schedule_compatibility = (shared_slots / total_slots) * 100.0

    # --- Factor 3: Participation rate ---
    sessions = group.sessions or []
    if sessions:
        n_members = len(active_members)
        attended_fractions = []
        for session in sessions:
            if session.attendance:
                attended = sum(1 for v in session.attendance.values() if v)
                attended_fractions.append(attended / max(n_members, 1))
        participation_rate = (
            float(np.mean(attended_fractions)) * 100.0
            if attended_fractions
            else 50.0
        )
    else:
        participation_rate = 50.0  # neutral when no sessions exist yet

    # --- Factor 4: Peer feedback score ---
    member_ids = [m.student_id for m in active_members]
    fb_result = await db.execute(
        select(func.avg(PeerFeedback.rating)).where(
            PeerFeedback.group_id == group_id,
            PeerFeedback.reviewee_id.in_(member_ids),
        )
    )
    avg_rating = fb_result.scalar_one_or_none()
    # avg_rating is on 1-5 scale → map to 0-100
    feedback_score = float(avg_rating) * 20.0 if avg_rating else 50.0

    # --- Weighted health score ---
    health_score = (
        skill_diversity * 0.25
        + schedule_compatibility * 0.30
        + participation_rate * 0.25
        + feedback_score * 0.20
    )

    # --- Recommendations ---
    recommendations: List[str] = []
    if skill_diversity < 40:
        recommendations.append(
            "Skill diversity is low — consider requesting a group rebalance to improve complementarity."
        )
    if schedule_compatibility < 30:
        recommendations.append(
            "Schedule overlap is limited — encourage members to update their availability."
        )
    if sessions and participation_rate < 50:
        recommendations.append(
            "Session attendance is below 50% — remind members about upcoming meetings."
        )
    if feedback_score < 40:
        recommendations.append(
            "Peer ratings are low — consider a group retrospective to surface and address issues."
        )
    if not recommendations:
        recommendations.append("Group is in good health — keep up the great work!")

    return GroupHealthResponse(
        group_id=group_id,
        health_score=round(health_score, 2),
        factors={
            "skill_diversity": round(skill_diversity, 2),
            "schedule_compatibility": round(schedule_compatibility, 2),
            "participation_rate": round(participation_rate, 2),
            "feedback_score": round(feedback_score, 2),
        },
        recommendations=recommendations,
    )


# ---------------------------------------------------------------------------
# Skill exchange map
# ---------------------------------------------------------------------------


def build_skill_exchange_map(
    group_members: List[Student],
) -> List[SkillExchangeItem]:
    """Produce a peer-teaching plan for the group.

    For each subject, the highest-rated member (≥ 6/10) is nominated as
    teacher for members who are weaker (< 5 or more than 2 points below the
    teacher).
    """
    if len(group_members) < 2:
        return []

    skills_by_student: Dict[uuid.UUID, Dict[str, int]] = {
        s.id: {sk.subject: sk.self_rating for sk in (s.skills or [])}
        for s in group_members
    }

    all_subjects: set[str] = set()
    for skills in skills_by_student.values():
        all_subjects.update(skills.keys())

    exchanges: List[SkillExchangeItem] = []

    for subject in all_subjects:
        # Identify best teacher
        best_teacher: Optional[Student] = None
        best_rating = -1
        for student in group_members:
            rating = skills_by_student[student.id].get(subject, 0)
            if rating > best_rating:
                best_rating = rating
                best_teacher = student

        if best_teacher is None or best_rating < 6:
            continue  # no qualified teacher for this subject

        for student in group_members:
            if student.id == best_teacher.id:
                continue
            learner_rating = skills_by_student[student.id].get(subject, 0)
            if learner_rating < 5 or (
                learner_rating > 0 and learner_rating < best_rating - 2
            ):
                exchanges.append(
                    SkillExchangeItem(
                        teacher_id=best_teacher.id,
                        teacher_name=best_teacher.full_name,
                        learner_id=student.id,
                        learner_name=student.full_name,
                        subject=subject,
                    )
                )

    return exchanges


# ---------------------------------------------------------------------------
# Suggested meeting times
# ---------------------------------------------------------------------------


def get_suggested_meeting_times(group_members: List[Student]) -> List[str]:
    """Return up to 5 time slots where ≥ 2 members are available.

    Each result is a human-readable string such as
    ``"Monday Morning (3/5 members)"``.
    """
    if not group_members:
        return []

    n_members = len(group_members)
    slot_counts: Dict[tuple, int] = {}

    for student in group_members:
        for avail in (student.availability or []):
            if avail.is_available:
                key = (avail.day_of_week, avail.slot.value)
                slot_counts[key] = slot_counts.get(key, 0) + 1

    valid = sorted(
        [(k, v) for k, v in slot_counts.items() if v >= 2],
        key=lambda x: x[1],
        reverse=True,
    )

    return [
        f"{_DAY_NAMES[day]} {_SLOT_LABELS.get(slot, slot.capitalize())} ({count}/{n_members} members)"
        for (day, slot), count in valid[:5]
    ]
