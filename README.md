# philiprehberger-json-logger

[![Tests](https://github.com/philiprehberger/py-json-logger/actions/workflows/publish.yml/badge.svg)](https://github.com/philiprehberger/py-json-logger/actions/workflows/publish.yml)
[![PyPI version](https://img.shields.io/pypi/v/philiprehberger-json-logger.svg)](https://pypi.org/project/philiprehberger-json-logger/)
[![License](https://img.shields.io/github/license/philiprehberger/py-json-logger)](LICENSE)

Drop-in structured JSON logging for Python using the stdlib `logging` module.

## Install

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

### Custom handler with JsonFormatter

```python
import logging
from philiprehberger_json_logger import JsonFormatter

handler = logging.FileHandler("app.log")
handler.setFormatter(JsonFormatter(extra_fields={"service": "worker"}))

logger = logging.getLogger("worker")
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

## API

| Name | Description |
|---|---|
| `JsonFormatter(*, extra_fields=None)` | Logging formatter that outputs JSON lines. `extra_fields` is a dict of static fields merged into every entry. |
| `setup(level="INFO", *, extra_fields=None, logger=None)` | Configure a logger with JSON output. Defaults to the root logger. Clears existing handlers. |

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

Any `extra={}` kwargs passed to the log call are merged into the top-level JSON object. Static `extra_fields` from the formatter are also merged.


## Development

```bash
pip install -e .
python -m pytest tests/ -v
```

## License

MIT
