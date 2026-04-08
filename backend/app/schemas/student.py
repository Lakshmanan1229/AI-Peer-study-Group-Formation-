from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------


class StudentRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=255)
    department: str = Field(pattern="^(CSE|IT|ECE)$")
    year: int = Field(ge=1, le=4)
    cgpa: float = Field(ge=0.0, le=10.0)
    learning_pace: str = Field(pattern="^(slow|moderate|fast)$")


class StudentLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------


class StudentProfile(BaseModel):
    id: uuid.UUID
    email: EmailStr
    full_name: str
    department: str
    year: int
    cgpa: float
    learning_pace: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class StudentProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    department: Optional[str] = Field(default=None, pattern="^(CSE|IT|ECE)$")
    year: Optional[int] = Field(default=None, ge=1, le=4)
    cgpa: Optional[float] = Field(default=None, ge=0.0, le=10.0)
    learning_pace: Optional[str] = Field(default=None, pattern="^(slow|moderate|fast)$")


# ---------------------------------------------------------------------------
# Skills
# ---------------------------------------------------------------------------


class SkillInput(BaseModel):
    subject: str = Field(min_length=1, max_length=255)
    self_rating: int = Field(ge=1, le=10)
    grade_points: Optional[float] = Field(default=None, ge=0.0)


class SkillBulkUpdate(BaseModel):
    skills: List[SkillInput] = Field(min_length=1)


class SkillResponse(BaseModel):
    subject: str
    self_rating: int
    peer_rating: Optional[float]
    grade_points: Optional[float]

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Availability
# ---------------------------------------------------------------------------


class AvailabilityInput(BaseModel):
    day_of_week: int = Field(ge=0, le=6)
    slot: str = Field(pattern="^(morning|afternoon|evening)$")
    is_available: bool


class AvailabilityBulkUpdate(BaseModel):
    slots: List[AvailabilityInput] = Field(min_length=1)


# ---------------------------------------------------------------------------
# Goals
# ---------------------------------------------------------------------------


class GoalUpdate(BaseModel):
    goals: str = Field(min_length=1, max_length=2000)
