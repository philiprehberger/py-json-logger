"""Drop-in structured JSON logging for Python using the stdlib logging module."""

from __future__ import annotations

import json
import logging
import traceback
from datetime import datetime, timezone
from typing import Any

__all__ = ["JsonFormatter", "setup"]

_BUILTIN_ATTRS = frozenset(logging.LogRecord("", 0, "", 0, None, None, None).__dict__)


class JsonFormatter(logging.Formatter):
    """Logging formatter that outputs JSON lines."""

    def __init__(self, *, extra_fields: dict[str, Any] | None = None) -> None:
        super().__init__()
        self._extra_fields = extra_fields or {}

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

        for key, value in record.__dict__.items():
            if key not in _BUILTIN_ATTRS and key not in entry:
                entry[key] = value

        return json.dumps(entry, default=str)


def setup(
    level: str | int = "INFO",
    *,
    extra_fields: dict[str, Any] | None = None,
    logger: logging.Logger | None = None,
) -> None:
    """Configure a logger with JSON output.

    Args:
        level: Log level name or constant.
        extra_fields: Static fields to include in every log entry.
        logger: Logger to configure. Defaults to the root logger.
    """
    target = logger or logging.getLogger()
    target.setLevel(level)

    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter(extra_fields=extra_fields))

    target.handlers.clear()
    target.addHandler(handler)
