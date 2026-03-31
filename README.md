# philiprehberger-json-logger

[![Tests](https://github.com/philiprehberger/py-json-logger/actions/workflows/publish.yml/badge.svg)](https://github.com/philiprehberger/py-json-logger/actions/workflows/publish.yml)
[![PyPI version](https://img.shields.io/pypi/v/philiprehberger-json-logger.svg)](https://pypi.org/project/philiprehberger-json-logger/)
[![Last updated](https://img.shields.io/github/last-commit/philiprehberger/py-json-logger)](https://github.com/philiprehberger/py-json-logger/commits/main)

Drop-in structured JSON logging for Python using the stdlib `logging` module.

## Installation

```bash
pip install philiprehberger-json-logger
```

## Usage

### Quick setup

```python
from philiprehberger_json_logger import setup

setup(level="DEBUG")

import logging
logging.info("Server started", extra={"port": 8080})
# {"timestamp": "2026-03-13T12:00:00+00:00", "level": "INFO", "message": "Server started", "logger": "root", "module": "app", "line": 5, "port": 8080}
```

### Named logger

```python
import logging
from philiprehberger_json_logger import setup

logger = logging.getLogger("myapp")
setup(level="INFO", logger=logger)

logger.warning("Disk usage high", extra={"usage_pct": 91.3})
```

### Static extra fields

```python
from philiprehberger_json_logger import setup

setup(level="INFO", extra_fields={"service": "api", "env": "production"})
```

Every log entry will include `"service": "api"` and `"env": "production"`.

### Field redaction

```python
from philiprehberger_json_logger import setup

setup(level="INFO", redact_fields={"password", "token", "secret"})

import logging
logging.info("Login", extra={"user": "alice", "password": "s3cret"})
# password field will appear as "***"
```

Redaction works recursively on nested dicts.

### Scoped context

```python
import logging
from philiprehberger_json_logger import setup, log_context

setup(level="INFO")

with log_context(request_id="abc-123", user="alice"):
    logging.info("Processing request")
    # log entry includes request_id and user fields

    with log_context(step="validation"):
        logging.info("Validating input")
        # log entry includes request_id, user, and step fields
```

### Custom handler with JsonFormatter

```python
import logging
from philiprehberger_json_logger import JsonFormatter

handler = logging.FileHandler("app.log")
handler.setFormatter(JsonFormatter(extra_fields={"service": "worker"}, redact_fields={"token"}))

logger = logging.getLogger("worker")
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

## API

| Name | Description |
|---|---|
| `JsonFormatter(*, extra_fields=None, redact_fields=None)` | Logging formatter that outputs JSON lines. `extra_fields` is a dict of static fields merged into every entry. `redact_fields` is a set of field names replaced with `"***"`. |
| `setup(level="INFO", *, extra_fields=None, redact_fields=None, logger=None)` | Configure a logger with JSON output. Defaults to the root logger. Clears existing handlers. |
| `log_context(**kwargs)` | Context manager that injects fields into all log entries within the block. Supports nesting. |

### JSON output fields

| Field | Description |
|---|---|
| `timestamp` | ISO 8601 UTC timestamp |
| `level` | Log level name (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`) |
| `message` | Formatted log message |
| `logger` | Logger name |
| `module` | Source module name |
| `line` | Source line number |
| `exception` | Full traceback string (only present when logging an exception) |

Any `extra={}` kwargs passed to the log call are merged into the top-level JSON object. Static `extra_fields` from the formatter and active `log_context()` fields are also merged.

## Development

```bash
pip install -e .
python -m pytest tests/ -v
```

## Support

If you find this project useful:

⭐ [Star the repo](https://github.com/philiprehberger/py-json-logger)

🐛 [Report issues](https://github.com/philiprehberger/py-json-logger/issues?q=is%3Aissue+is%3Aopen+label%3Abug)

💡 [Suggest features](https://github.com/philiprehberger/py-json-logger/issues?q=is%3Aissue+is%3Aopen+label%3Aenhancement)

❤️ [Sponsor development](https://github.com/sponsors/philiprehberger)

🌐 [All Open Source Projects](https://philiprehberger.com/open-source-packages)

💻 [GitHub Profile](https://github.com/philiprehberger)

🔗 [LinkedIn Profile](https://www.linkedin.com/in/philiprehberger)

## License

[MIT](LICENSE)
