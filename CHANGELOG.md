# Changelog

## 0.2.0 (2026-03-27)

- Add field redaction via `redact_fields` parameter on `JsonFormatter` and `setup()`
- Add `log_context()` context manager for scoped structured fields using `contextvars`
- Nested dict values are recursively redacted when matching `redact_fields`
- Nested `log_context()` blocks merge and inner values override outer ones

## 0.1.5 (2026-03-22)

- Add pytest and mypy configuration to pyproject.toml

## 0.1.3

- Add Development section to README

## 0.1.0 (2026-03-13)

- Initial release
- `JsonFormatter` for structured JSON log output
- `setup()` for quick root logger configuration
- Exception traceback included as `exception` field
- Static `extra_fields` support
- Extra record attributes merged into JSON output
