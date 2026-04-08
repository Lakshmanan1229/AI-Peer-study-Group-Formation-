"""Security utilities: password hashing and JWT token management.

These functions are thin wrappers around ``passlib`` (bcrypt) and
``python-jose`` (JWT) that standardise token creation and validation
for the entire application.
"""
from __future__ import annotations

from datetime import timedelta, timezone, datetime
from typing import Any, Dict, Optional

from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ──────────────────────────────────────────────────────────────────────────────
# Password utilities
# ──────────────────────────────────────────────────────────────────────────────


def hash_password(plain_password: str) -> str:
    """Return a bcrypt hash of *plain_password*."""
    return _pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return ``True`` if *plain_password* matches *hashed_password*."""
    return _pwd_context.verify(plain_password, hashed_password)


# ──────────────────────────────────────────────────────────────────────────────
# Token utilities
# ──────────────────────────────────────────────────────────────────────────────


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a signed JWT access token.

    Args:
        data: payload claims to embed (``sub`` should be the student id string).
        expires_delta: custom lifetime; defaults to ``ACCESS_TOKEN_EXPIRE_MINUTES``.

    Returns:
        Encoded JWT string.
    """
    payload = dict(data)
    expire = datetime.now(timezone.utc) + (
        expires_delta
        if expires_delta is not None
        else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload.update({"exp": expire, "type": "access"})
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create a signed JWT refresh token with a longer lifetime.

    Args:
        data: payload claims (``sub`` should be the student id string).

    Returns:
        Encoded JWT string.
    """
    payload = dict(data)
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    payload.update({"exp": expire, "type": "refresh"})
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> Dict[str, Any]:
    """Decode and verify a JWT token.

    Args:
        token: raw JWT string.

    Returns:
        Decoded payload dict.

    Raises:
        :class:`fastapi.HTTPException` 401 if the token is invalid or expired.
    """
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
