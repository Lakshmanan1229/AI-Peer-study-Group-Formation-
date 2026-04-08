from pydantic import BaseModel
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.rate_limit import limiter
from app.schemas.student import StudentLogin, StudentRegister, TokenResponse
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


class _RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def register(
    request: Request,
    student_data: StudentRegister,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Register a new student account and return a JWT token pair."""
    return await auth_service.register_student(db, student_data)


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
async def login(
    request: Request,
    credentials: StudentLogin,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Authenticate with email + password and return a JWT token pair."""
    return await auth_service.authenticate_student(
        db, credentials.email, credentials.password
    )


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit("20/minute")
async def refresh(
    request: Request,
    body: _RefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Exchange a valid refresh token for a new token pair."""
    return await auth_service.refresh_tokens(db, body.refresh_token)

