"""Study-group-related ORM models and enumerations."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    Uuid,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class GroupStatusEnum(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    disbanded = "disbanded"


class MemberRoleEnum(str, enum.Enum):
    member = "member"
    leader = "leader"


class SessionTypeEnum(str, enum.Enum):
    online = "online"
    offline = "offline"


# ---------------------------------------------------------------------------
# StudyGroup
# ---------------------------------------------------------------------------

class StudyGroup(Base):
    __tablename__ = "study_groups"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4, index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    department: Mapped[str] = mapped_column(String(10), nullable=False)
    status: Mapped[GroupStatusEnum] = mapped_column(
        Enum(GroupStatusEnum, name="group_status_enum", create_type=False),
        nullable=False,
        server_default="active",
    )
    max_size: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="6",
    )
    complementary_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    schedule_overlap_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    goal_similarity_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"),
    )

    # Relationships
    memberships: Mapped[list[GroupMembership]] = relationship(
        "GroupMembership", back_populates="group", cascade="all, delete-orphan",
    )
    sessions: Mapped[list[GroupSession]] = relationship(
        "GroupSession", back_populates="group", cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<StudyGroup {self.name} ({self.department})>"


# ---------------------------------------------------------------------------
# GroupMembership
# ---------------------------------------------------------------------------

class GroupMembership(Base):
    __tablename__ = "group_memberships"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    group_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("study_groups.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[MemberRoleEnum] = mapped_column(
        Enum(MemberRoleEnum, name="member_role_enum", create_type=False),
        nullable=False,
        server_default="member",
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"),
    )
    left_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )

    # Relationships
    group: Mapped[StudyGroup] = relationship("StudyGroup", back_populates="memberships")
    student: Mapped["Student"] = relationship("Student", back_populates="group_memberships")

    def __repr__(self) -> str:
        return f"<GroupMembership group={self.group_id} student={self.student_id}>"


# Avoid circular import — use TYPE_CHECKING or string annotation
from app.models.student import Student  # noqa: E402, F401


# ---------------------------------------------------------------------------
# GroupSession
# ---------------------------------------------------------------------------

class GroupSession(Base):
    __tablename__ = "group_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4, index=True,
    )
    group_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("study_groups.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    scheduled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
    )
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    location: Mapped[str | None] = mapped_column(String(500), nullable=True)
    session_type: Mapped[SessionTypeEnum] = mapped_column(
        Enum(SessionTypeEnum, name="session_type_enum", create_type=False),
        nullable=False,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    attendance: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("students.id", ondelete="SET NULL"),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"),
    )

    # Relationships
    group: Mapped[StudyGroup] = relationship("StudyGroup", back_populates="sessions")

    def __repr__(self) -> str:
        return f"<GroupSession {self.id} group={self.group_id}>"
