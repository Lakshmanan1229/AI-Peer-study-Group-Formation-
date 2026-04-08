"""Request ID middleware for distributed tracing.

Attaches a unique ``X-Request-ID`` header to every response.  If the
incoming request already carries the header (e.g. from an API gateway or
load balancer), its value is reused.
"""
from __future__ import annotations

import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        # Stash on request.state so downstream code can access it
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
