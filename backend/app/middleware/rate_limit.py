"""API rate limiting middleware using slowapi.

Defaults:
  - 60 requests/minute per IP for general endpoints
  - 10 requests/minute per IP for auth endpoints (login/register)

The limiter uses an in-memory backend by default. In production, set
``REDIS_URL`` to use Redis as the backend for shared state across workers.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["60/minute"],
    storage_uri=None,  # in-memory; override with Redis URI in production
)
