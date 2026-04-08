from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.middleware.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.student import AvailabilitySlot, SlotEnum, Student
from app.schemas.student import StudentRegister, TokenResponse


async def register_student(
    db: AsyncSession,
    student_data: StudentRegister,
) -> TokenResponse:
    """Create a new student account and return a fresh token pair.

    Raises:
        HTTPException 400: if the email is already registered.
    """
    result = await db.execute(
        select(Student).where(Student.email == student_data.email)
    )
    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered.",
        )

    student = Student(
        email=student_data.email,
        hashed_password=hash_password(student_data.password),
        full_name=student_data.full_name,
        department=student_data.department,
        year=student_data.year,
        cgpa=student_data.cgpa,
        learning_pace=student_data.learning_pace,
    )
    db.add(student)
    await db.flush()  # populate student.id before creating FK rows

    # Create all 21 default availability slots (all False)
    for day in range(7):
        for slot in SlotEnum:
            db.add(
                AvailabilitySlot(
                    student_id=student.id,
                    day_of_week=day,
                    slot=slot,
                    is_available=False,
                )
            )

    await db.commit()
    await db.refresh(student)

    subject = str(student.id)
    return TokenResponse(
        access_token=create_access_token(subject),
        refresh_token=create_refresh_token(subject),
    )


async def authenticate_student(
    db: AsyncSession,
    email: str,
    password: str,
) -> TokenResponse:
    """Verify credentials and return a fresh token pair.

    Raises:
        HTTPException 401: on invalid credentials.
        HTTPException 403: if the account is inactive.
    """
    result = await db.execute(select(Student).where(Student.email == email))
    student = result.scalar_one_or_none()

    if student is None or not verify_password(password, student.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not student.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated.",
        )

    subject = str(student.id)
    return TokenResponse(
        access_token=create_access_token(subject),
        refresh_token=create_refresh_token(subject),
    )


async def refresh_tokens(
    db: AsyncSession,
    refresh_token: str,
) -> TokenResponse:
    """Issue a new token pair using a valid refresh token.

    Raises:
        HTTPException 401: on invalid / expired token or unknown student.
    """
    payload = decode_token(refresh_token)

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is not a refresh token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    student_id_str: str | None = payload.get("sub")
    if not student_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token subject missing.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        student_id = uuid.UUID(student_id_str)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token subject.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    result = await db.execute(select(Student).where(Student.id == student_id))
    student = result.scalar_one_or_none()
    if student is None or not student.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Student not found or inactive.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    subject = str(student.id)
    return TokenResponse(
        access_token=create_access_token(subject),
        refresh_token=create_refresh_token(subject),
    )
