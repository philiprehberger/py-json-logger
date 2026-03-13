from __future__ import annotations

import io
import json
import logging

from philiprehberger_json_logger import JsonFormatter, setup


def _make_logger(
    name: str | None = None,
    *,
    extra_fields: dict | None = None,
) -> tuple[logging.Logger, io.StringIO]:
    """Create a logger that writes to a StringIO buffer and return both."""
    buf = io.StringIO()
    logger = logging.getLogger(name)
    logger.handlers.clear()
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(buf)
    handler.setFormatter(JsonFormatter(extra_fields=extra_fields))
    logger.addHandler(handler)
    return logger, buf


def _parse(buf: io.StringIO) -> dict:
    """Parse the first JSON line from the buffer."""
    buf.seek(0)
    return json.loads(buf.readline())


def test_setup_configures_root_logger() -> None:
    root = logging.getLogger()
    original_handlers = list(root.handlers)
    try:
        setup(level="WARNING")
        assert root.level == logging.WARNING
        assert len(root.handlers) == 1
        assert isinstance(root.handlers[0].formatter, JsonFormatter)
    finally:
        root.handlers = original_handlers


def test_setup_configures_named_logger() -> None:
    logger = logging.getLogger("test.named")
    logger.handlers.clear()
    setup(level="DEBUG", logger=logger)
    assert logger.level == logging.DEBUG
    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0].formatter, JsonFormatter)
    logger.handlers.clear()


def test_output_is_valid_json() -> None:
    logger, buf = _make_logger("test.valid_json")
    logger.info("hello")
    buf.seek(0)
    line = buf.readline()
    parsed = json.loads(line)
    assert isinstance(parsed, dict)
    logger.handlers.clear()


def test_timestamp_present_and_iso_format() -> None:
    logger, buf = _make_logger("test.timestamp")
    logger.info("check timestamp")
    entry = _parse(buf)
    assert "timestamp" in entry
    assert "T" in entry["timestamp"]
    assert entry["timestamp"].endswith("+00:00")
    logger.handlers.clear()


def test_level_info() -> None:
    logger, buf = _make_logger("test.level_info")
    logger.info("info msg")
    assert _parse(buf)["level"] == "INFO"
    logger.handlers.clear()


def test_level_warning() -> None:
    logger, buf = _make_logger("test.level_warning")
    logger.warning("warn msg")
    assert _parse(buf)["level"] == "WARNING"
    logger.handlers.clear()


def test_level_error() -> None:
    logger, buf = _make_logger("test.level_error")
    logger.error("error msg")
    assert _parse(buf)["level"] == "ERROR"
    logger.handlers.clear()


def test_level_debug() -> None:
    logger, buf = _make_logger("test.level_debug")
    logger.debug("debug msg")
    assert _parse(buf)["level"] == "DEBUG"
    logger.handlers.clear()


def test_message_field_correct() -> None:
    logger, buf = _make_logger("test.message")
    logger.info("expected message")
    assert _parse(buf)["message"] == "expected message"
    logger.handlers.clear()


def test_logger_name_field() -> None:
    logger, buf = _make_logger("test.loggername")
    logger.info("hi")
    assert _parse(buf)["logger"] == "test.loggername"
    logger.handlers.clear()


def test_module_and_line_present() -> None:
    logger, buf = _make_logger("test.module_line")
    logger.info("check fields")
    entry = _parse(buf)
    assert "module" in entry
    assert "line" in entry
    assert isinstance(entry["line"], int)
    logger.handlers.clear()


def test_exception_field_on_error() -> None:
    logger, buf = _make_logger("test.exception")
    try:
        raise ValueError("boom")
    except ValueError:
        logger.exception("something failed")
    entry = _parse(buf)
    assert "exception" in entry
    assert "ValueError: boom" in entry["exception"]
    assert "Traceback" in entry["exception"]
    logger.handlers.clear()


def test_extra_fields_merged() -> None:
    logger, buf = _make_logger("test.extra_fields", extra_fields={"service": "api", "env": "test"})
    logger.info("with extras")
    entry = _parse(buf)
    assert entry["service"] == "api"
    assert entry["env"] == "test"
    logger.handlers.clear()


def test_extra_record_attributes() -> None:
    logger, buf = _make_logger("test.record_extra")
    logger.info("with request", extra={"request_id": "abc-123"})
    entry = _parse(buf)
    assert entry["request_id"] == "abc-123"
    logger.handlers.clear()


def test_multiple_log_calls_produce_separate_lines() -> None:
    logger, buf = _make_logger("test.multiline")
    logger.info("first")
    logger.info("second")
    logger.info("third")
    buf.seek(0)
    lines = [line for line in buf.readlines() if line.strip()]
    assert len(lines) == 3
    for line in lines:
        parsed = json.loads(line)
        assert "message" in parsed
    logger.handlers.clear()


def test_setup_clears_existing_handlers() -> None:
    logger = logging.getLogger("test.clear_handlers")
    logger.handlers.clear()
    logger.addHandler(logging.StreamHandler())
    logger.addHandler(logging.StreamHandler())
    assert len(logger.handlers) == 2
    setup(logger=logger)
    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0].formatter, JsonFormatter)
    logger.handlers.clear()


def test_json_formatter_standalone_with_custom_handler() -> None:
    buf = io.StringIO()
    handler = logging.StreamHandler(buf)
    handler.setFormatter(JsonFormatter(extra_fields={"component": "worker"}))

    logger = logging.getLogger("test.standalone")
    logger.handlers.clear()
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    logger.info("standalone test")
    entry = _parse(buf)
    assert entry["message"] == "standalone test"
    assert entry["component"] == "worker"
    logger.handlers.clear()
