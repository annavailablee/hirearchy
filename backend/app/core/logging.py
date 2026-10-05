"""
Structured JSON logging.

Why JSON: log aggregators (Datadog, Loki, CloudWatch) parse structured fields
natively. `grep 404` beats `grep "HTTP/1.1\" 404"` any day.
"""
import json
import logging
import sys
from datetime import UTC, datetime

from app.config import settings


class JsonFormatter(logging.Formatter):
    """Format every record as a single-line JSON object."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        # Optional context added via `extra=...`
        for key in ("request_id", "method", "path", "status_code", "duration_ms"):
            if hasattr(record, key):
                payload[key] = getattr(record, key)

        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str)


def configure_logging() -> None:
    """
    Replace the root logger's handlers with a single JSON stream handler.
    Idempotent — safe to call more than once.
    """
    root = logging.getLogger()
    # Remove pre-existing handlers (uvicorn installs its own on import).
    for h in list(root.handlers):
        root.removeHandler(h)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root.addHandler(handler)

    # Default level. In production you'd set via env var.
    level = logging.DEBUG if settings.environment == "development" else logging.INFO
    root.setLevel(level)

    # uvicorn's loggers propagate to root by default, but it also installs
    # its own access logger. Silence that in favor of our request middleware.
    logging.getLogger("uvicorn.access").disabled = True