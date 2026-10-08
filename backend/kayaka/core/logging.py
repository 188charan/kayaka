"""Logging configuration: JSON lines in deployed environments, readable lines locally.

Every record gets a `request_id` attribute (or "-") so it can be correlated with the
X-Request-ID response header and the `requestId` field in error bodies. JSON output uses
`severity` and `timestamp` keys, which Google Cloud Logging understands natively.
"""

import logging
from typing import Any

from kayaka.core.context import get_request_id


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = get_request_id() or "-"
        return True


def build_logging_config(*, level: str = "INFO", fmt: str = "json") -> dict[str, Any]:
    formatter = "json" if fmt == "json" else "console"
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "request_id": {"()": "kayaka.core.logging.RequestIdFilter"},
        },
        "formatters": {
            "json": {
                "()": "pythonjsonlogger.json.JsonFormatter",
                "fmt": "%(asctime)s %(levelname)s %(name)s %(message)s %(request_id)s",
                "rename_fields": {"asctime": "timestamp", "levelname": "severity"},
            },
            "console": {
                "format": "%(asctime)s %(levelname)-7s [%(request_id)s] %(name)s: %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "filters": ["request_id"],
                "formatter": formatter,
            },
        },
        "root": {"handlers": ["console"], "level": level},
        "loggers": {
            # 4xx are already covered by our access log; keep django.request for 5xx tracebacks.
            "django.request": {"level": "ERROR"},
            "django.db.backends": {"level": "WARNING"},
            # runserver's own access lines duplicate kayaka.request.
            "django.server": {"level": "WARNING"},
        },
    }
