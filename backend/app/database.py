from __future__ import annotations

import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

logger = logging.getLogger(__name__)

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.ENVIRONMENT == "development",
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Create all tables that do not yet exist.

    Called once at application startup.  Production deployments should prefer
    Alembic migrations; this function is primarily useful in development and
    testing.
    """
    from app.models import (  # noqa: F401 – import triggers mapper registration
        AvailabilitySlot,
        GroupMembership,
        GroupSession,
        PeerFeedback,
        SkillAssessment,
        Student,
        StudyGroup,
    )

    async with engine.begin() as conn:
        try:
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created / verified successfully.")
        except Exception as exc:
            logger.exception("Failed to initialise database tables: %s", exc)
            raise
