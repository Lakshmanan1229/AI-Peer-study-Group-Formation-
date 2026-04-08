"""Structured JSON logging configuration.

Call ``setup_logging()`` once at application startup to switch the root
logger to JSON format (suitable for CloudWatch / ELK) in non-development
environments.
"""
from __future__ import annotations

import logging
import sys

from app.config import settings


class JSONFormatter(logging.Formatter):
    """Emit each log record as a single-line JSON object."""

    def format(self, record: logging.LogRecord) -> str:
        import json
        log_entry = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info and record.exc_info[0]:
            log_entry["exception"] = self.formatException(record.exc_info)
        # Attach request_id if present
        request_id = getattr(record, "request_id", None)
        if request_id:
            log_entry["request_id"] = request_id
        return json.dumps(log_entry, default=str)


def setup_logging() -> None:
    """Configure the root logger.

    In ``development`` mode the default human-readable format is kept.
    In ``staging`` / ``production`` a JSON formatter is used.
    """
    level = logging.DEBUG if settings.ENVIRONMENT == "development" else logging.INFO
    root = logging.getLogger()
    root.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    if settings.ENVIRONMENT != "development":
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
        ))
    root.handlers = [handler]
