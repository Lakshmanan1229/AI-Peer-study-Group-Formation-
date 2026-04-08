from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.database import init_db
from app.middleware.logging_config import setup_logging
from app.middleware.rate_limit import limiter
from app.middleware.request_id import RequestIDMiddleware

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Lazy router imports (routers will be created in their own modules)
# ---------------------------------------------------------------------------
from app.routers import admin, auth, feedback, groups, recommendations, students


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Startup and shutdown lifecycle handler."""
    setup_logging()
    logger.info("Starting up AI Peer Study Group Formation API…")
    await init_db()
    logger.info("Database initialised.")
    yield
    logger.info("Shutting down AI Peer Study Group Formation API.")


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Peer Study Group Formation API",
        description="Backend service for intelligent peer study group formation and management.",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # ------------------------------------------------------------------
    # Rate limiter
    # ------------------------------------------------------------------
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # ------------------------------------------------------------------
    # Request ID middleware (adds X-Request-ID to every response)
    # ------------------------------------------------------------------
    app.add_middleware(RequestIDMiddleware)

    # ------------------------------------------------------------------
    # CORS
    # allow_credentials=True requires explicit origins (not "*").
    # In development we use ALLOWED_ORIGINS from settings (which covers
    # localhost variants). Wildcard "*" is intentionally avoided because
    # browsers reject credentialed requests to wildcard origins.
    # ------------------------------------------------------------------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ------------------------------------------------------------------
    # Routers
    # ------------------------------------------------------------------
    app.include_router(auth.router, prefix="/v1")
    app.include_router(students.router, prefix="/v1")
    app.include_router(groups.router, prefix="/v1")
    app.include_router(feedback.router, prefix="/v1")
    app.include_router(recommendations.router, prefix="/v1")
    app.include_router(admin.router, prefix="/v1")

    # ------------------------------------------------------------------
    # Core endpoints
    # ------------------------------------------------------------------

    @app.get("/health", tags=["System"], summary="Health check")
    async def health_check() -> JSONResponse:
        return JSONResponse(
            content={"status": "ok", "environment": settings.ENVIRONMENT},
            status_code=200,
        )

    @app.get("/", tags=["System"], summary="Root")
    async def root() -> JSONResponse:
        return JSONResponse(
            content={
                "service": "AI Peer Study Group Formation API",
                "version": "1.0.0",
                "docs": "/docs",
            }
        )

    return app


app: FastAPI = create_app()
