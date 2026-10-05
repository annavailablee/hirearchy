"""
Request-scoped middleware: assigns a request ID, logs every request,
and echoes the ID in the response header.
"""
import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger("app.request")


class RequestContextMiddleware(BaseHTTPMiddleware):
    """
    For every request:
    1. Assign or accept a request ID (from incoming X-Request-ID header).
    2. Time the request.
    3. Log method, path, status, duration with the request ID.
    4. Echo the request ID back in the response header.
    """

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        # Store on request.state so endpoints can access it if needed.
        request.state.request_id = request_id

        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            # The exception itself is logged by FastAPI's error handler.
            # We log that we saw it, with the request ID, so the trace is complete.
            duration_ms = round((time.perf_counter() - start) * 1000, 1)
            logger.exception(
                "Request failed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": duration_ms,
                },
            )
            raise

        duration_ms = round((time.perf_counter() - start) * 1000, 1)
        response.headers["X-Request-ID"] = request_id

        logger.info(
            "Request completed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )
        return response