"""Drop-in structured JSON logging for Python using the stdlib logging module."""

from __future__ import annotations

import contextlib
import contextvars
import json
import logging
import traceback
from collections.abc import Generator
from datetime import datetime, timezone
from typing import Any

__all__ = ["JsonFormatter", "log_context", "setup"]

_BUILTIN_ATTRS = frozenset(logging.LogRecord("", 0, "", 0, None, None, None).__dict__)

_context_var: contextvars.ContextVar[dict[str, Any]] = contextvars.ContextVar(
    "log_context", default={}
)


@contextlib.contextmanager
def log_context(**kwargs: Any) -> Generator[None, None, None]:
    """Context manager that injects fields into all log entries within the block.

    Usage::

        with log_context(request_id="abc-123", user="alice"):
            logging.info("Processing request")
            # log entry will include request_id and user fields

    Contexts can be nested; inner values override outer ones.
    """
    previous = _context_var.get()
    merged = {**previous, **kwargs}
    token = _context_var.set(merged)
    try:
        yield
    finally:
        _context_var.reset(token)


def _redact(data: dict[str, Any], fields: set[str]) -> dict[str, Any]:
    """Recursively redact values for keys matching *fields*."""
    redacted: dict[str, Any] = {}
    for key, value in data.items():
        if key in fields:
            redacted[key] = "***"
        elif isinstance(value, dict):
            redacted[key] = _redact(value, fields)
        else:
            redacted[key] = value
    return redacted


class JsonFormatter(logging.Formatter):
    """Logging formatter that outputs JSON lines."""

    def __init__(
        self,
        *,
        extra_fields: dict[str, Any] | None = None,
        redact_fields: set[str] | None = None,
    ) -> None:
        super().__init__()
        self._extra_fields = extra_fields or {}
        self._redact_fields = redact_fields or set()

    def format(self, record: logging.LogRecord) -> str:
        entry: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "module": record.module,
            "line": record.lineno,
        }

        if record.exc_info and record.exc_info[0] is not None:
            entry["exception"] = "".join(traceback.format_exception(*record.exc_info))

        if self._extra_fields:
            entry.update(self._extra_fields)

        # Merge context vars
        ctx = _context_var.get()
        if ctx:
            entry.update(ctx)

        for key, value in record.__dict__.items():
            if key not in _BUILTIN_ATTRS and key not in entry:
                entry[key] = value

        # Redact sensitive fields
        if self._redact_fields:
            entry = _redact(entry, self._redact_fields)

        return json.dumps(entry, default=str)


def setup(
    level: str | int = "INFO",
    *,
    extra_fields: dict[str, Any] | None = None,
    redact_fields: set[str] | None = None,
    logger: logging.Logger | None = None,
) -> None:
    """Configure a logger with JSON output.

    Args:
        level: Log level name or constant.
        extra_fields: Static fields to include in every log entry.
        redact_fields: Set of field names whose values will be replaced with ``"***"``.
        logger: Logger to configure. Defaults to the root logger.
    """
    target = logger or logging.getLogger()
    target.setLevel(level)

    handler = logging.StreamHandler()
    handler.setFormatter(
        JsonFormatter(extra_fields=extra_fields, redact_fields=redact_fields)
    )

    target.handlers.clear()
    target.addHandler(handler)
