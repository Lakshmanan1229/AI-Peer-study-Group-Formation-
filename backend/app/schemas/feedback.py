from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Submission
# ---------------------------------------------------------------------------


class FeedbackSubmit(BaseModel):
    reviewee_id: uuid.UUID
    rating: int = Field(ge=1, le=5)
    helpfulness_score: int = Field(ge=1, le=5)
    comment: str = Field(default="", max_length=5000)
    is_anonymous: bool = False


class FeedbackBulkSubmit(BaseModel):
    feedbacks: List[FeedbackSubmit] = Field(min_length=1)
    session_id: Optional[uuid.UUID] = None


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------


class GroupReportResponse(BaseModel):
    group_id: uuid.UUID
    avg_rating: float
    avg_helpfulness: float
    member_reports: List[Dict[str, Any]] = Field(default_factory=list)
    total_sessions: int
