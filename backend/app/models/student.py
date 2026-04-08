"""Student-related ORM models and enumerations."""

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
    String,
    Text,
    text,
)
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class DepartmentEnum(str, enum.Enum):
    CSE = "CSE"
    IT = "IT"
    ECE = "ECE"


class LearningPaceEnum(str, enum.Enum):
    slow = "slow"
    moderate = "moderate"
    fast = "fast"


class RoleEnum(str, enum.Enum):
    student = "student"
    admin = "admin"
    faculty = "faculty"


class SlotEnum(str, enum.Enum):
    morning = "morning"
    afternoon = "afternoon"
    evening = "evening"


# ---------------------------------------------------------------------------
# Student
# ---------------------------------------------------------------------------

class Student(Base):
    __tablename__ = "students"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4, index=True,
    )
    email: Mapped[str] = mapped_column(
        String(320), unique=True, nullable=False, index=True,
    )
    hashed_password: Mapped[str] = mapped_column(String(1024), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    department: Mapped[DepartmentEnum] = mapped_column(
        Enum(DepartmentEnum, name="department_enum", create_type=False),
        nullable=False,
    )
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    cgpa: Mapped[float] = mapped_column(Float, nullable=False)
    learning_pace: Mapped[LearningPaceEnum] = mapped_column(
        Enum(LearningPaceEnum, name="learning_pace_enum", create_type=False),
        nullable=False,
    )
    role: Mapped[RoleEnum] = mapped_column(
        Enum(RoleEnum, name="role_enum", create_type=False),
        nullable=False,
        server_default="student",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("1"),
    )
    goals: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    goal_embedding: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"),
    )

    # Relationships
    skills: Mapped[list[SkillAssessment]] = relationship(
        "SkillAssessment", back_populates="student", cascade="all, delete-orphan",
    )
    availability_slots: Mapped[list[AvailabilitySlot]] = relationship(
        "AvailabilitySlot", back_populates="student", cascade="all, delete-orphan",
    )
    group_memberships: Mapped[list] = relationship(
        "GroupMembership", back_populates="student", cascade="all, delete-orphan",
    )

    @property
    def availability(self) -> list[AvailabilitySlot]:
        """Alias for availability_slots used by service layer."""
        return self.availability_slots

    def __repr__(self) -> str:
        return f"<Student {self.email} ({self.department.value})>"


# ---------------------------------------------------------------------------
# SkillAssessment
# ---------------------------------------------------------------------------

class SkillAssessment(Base):
    __tablename__ = "skill_assessments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    self_rating: Mapped[int] = mapped_column(Integer, nullable=False)
    peer_rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    grade_points: Mapped[float | None] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"),
    )

    # Relationships
    student: Mapped[Student] = relationship("Student", back_populates="skills")

    def __repr__(self) -> str:
        return f"<SkillAssessment {self.subject} student={self.student_id}>"


# ---------------------------------------------------------------------------
# AvailabilitySlot
# ---------------------------------------------------------------------------

class AvailabilitySlot(Base):
    __tablename__ = "availability_slots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)
    slot: Mapped[SlotEnum] = mapped_column(
        Enum(SlotEnum, name="slot_enum", create_type=False),
        nullable=False,
    )
    is_available: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("0"),
    )

    # Relationships
    student: Mapped[Student] = relationship("Student", back_populates="availability_slots")

    def __repr__(self) -> str:
        return f"<AvailabilitySlot day={self.day_of_week} slot={self.slot.value}>"
