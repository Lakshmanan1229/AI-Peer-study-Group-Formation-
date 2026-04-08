"""Peer-feedback ORM model."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Text,
    text,
)
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class PeerFeedback(Base):
    __tablename__ = "peer_feedbacks"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4, index=True,
    )
    reviewer_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    reviewee_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    group_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("study_groups.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    session_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("group_sessions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    helpfulness_score: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_anonymous: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("0"),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"),
    )

    def __repr__(self) -> str:
        return (
            f"<PeerFeedback reviewer={self.reviewer_id} "
            f"reviewee={self.reviewee_id}>"
        )
