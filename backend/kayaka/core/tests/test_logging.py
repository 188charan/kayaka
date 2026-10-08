import io
import json
import logging
import logging.config

import pytest
from django.conf import settings

from kayaka.core.context import reset_request_id, set_request_id
from kayaka.core.logging import build_logging_config


@pytest.fixture(autouse=True)
def restore_logging():
    yield
    logging.config.dictConfig(settings.LOGGING)


def capture(fmt):
    config = build_logging_config(level="INFO", fmt=fmt)
    logging.config.dictConfig(config)
    handler = logging.getLogger().handlers[0]
    assert isinstance(handler, logging.StreamHandler)
    stream = io.StringIO()
    handler.setStream(stream)
    return stream


def test_json_log_lines_include_request_id_and_severity():
    stream = capture("json")
    token = set_request_id("req_abc12345")
    try:
        logging.getLogger("kayaka.test").info("hello", extra={"status": 200})
    finally:
        reset_request_id(token)
    line = json.loads(stream.getvalue().strip().splitlines()[-1])
    assert line["message"] == "hello"
    assert line["severity"] == "INFO"
    assert line["request_id"] == "req_abc12345"
    assert line["status"] == 200
    assert "timestamp" in line


def test_console_format_is_human_readable():
    stream = capture("console")
    logging.getLogger("kayaka.test").warning("careful")
    assert "WARNING" in stream.getvalue()
    assert "[-] kayaka.test: careful" in stream.getvalue()
