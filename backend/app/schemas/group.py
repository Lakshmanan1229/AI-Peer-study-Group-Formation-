from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Members
# ---------------------------------------------------------------------------


class GroupMemberInfo(BaseModel):
    id: uuid.UUID
    full_name: str
    department: str
    year: int
    cgpa: float
    learning_pace: str
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Group detail
# ---------------------------------------------------------------------------


class GroupDetail(BaseModel):
    id: uuid.UUID
    name: str
    department: str
    status: str
    members: List[GroupMemberInfo] = Field(default_factory=list)
    complementary_score: Optional[float] = None
    schedule_overlap_count: Optional[int] = None
    goal_similarity_score: Optional[float] = None
    suggested_meeting_times: List[str] = Field(default_factory=list)

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Group health
# ---------------------------------------------------------------------------


class GroupHealthResponse(BaseModel):
    group_id: uuid.UUID
    health_score: float = Field(ge=0, le=100, description="Overall health score 0–100")
    factors: Dict[str, Any] = Field(
        default_factory=dict,
        description="Breakdown of individual health factors",
    )
    recommendations: List[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Sessions
# ---------------------------------------------------------------------------


class SessionCreate(BaseModel):
    scheduled_at: datetime
    duration_minutes: int = Field(ge=15, le=480)
    location: Optional[str] = Field(default=None, max_length=500)
    session_type: str = Field(pattern="^(online|offline)$")
    notes: Optional[str] = Field(default=None, max_length=5000)


# ---------------------------------------------------------------------------
# Skill exchange
# ---------------------------------------------------------------------------


class SkillExchangeItem(BaseModel):
    teacher_id: uuid.UUID
    teacher_name: str
    learner_id: uuid.UUID
    learner_name: str
    subject: str
