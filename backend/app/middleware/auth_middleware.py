"""FastAPI dependency functions for authentication and authorization.

This module re-exports and extends the core auth primitives from
``app.middleware.security``, adding role-based access guards.
"""
from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.database import get_db
from app.middleware.security import decode_token, get_current_student

_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/login")


async def require_admin(
    current_student=Depends(get_current_student),
):
    """Raise HTTP 403 unless the authenticated student has the *admin* role.

    Usage::

        @router.get("/admin-only")
        async def admin_endpoint(admin = Depends(require_admin)):
            ...
    """
    from app.models.student import RoleEnum

    if current_student.role != RoleEnum.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required.",
        )
    return current_student


async def require_faculty(
    current_student=Depends(get_current_student),
):
    """Raise HTTP 403 unless the student's role is *admin* or *faculty*.

    Usage::

        @router.get("/faculty-only")
        async def faculty_endpoint(staff = Depends(require_faculty)):
            ...
    """
    from app.models.student import RoleEnum

    if current_student.role not in (RoleEnum.admin, RoleEnum.faculty):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Faculty or admin privileges required.",
        )
    return current_student


# Re-export for convenience so callers can import everything from this module.
__all__ = [
    "get_current_student",
    "require_admin",
    "require_faculty",
]
