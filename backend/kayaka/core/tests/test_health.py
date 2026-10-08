from unittest import mock

import pytest
from django.db import OperationalError


def test_healthz_is_ok_without_touching_the_database(client):
    # No django_db mark: any database access would fail this test.
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert "no-cache" in response["Cache-Control"]


@pytest.mark.django_db
def test_readyz_checks_the_database(client):
    response = client.get("/readyz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "checks": {"database": "ok"}}


@pytest.mark.django_db
def test_readyz_returns_503_when_database_is_unavailable(client):
    with mock.patch(
        "kayaka.core.health.connection.cursor",
        side_effect=OperationalError("connection refused"),
    ):
        response = client.get("/readyz")
    assert response.status_code == 503
    assert response.json() == {"status": "unavailable", "checks": {"database": "error"}}


def test_health_responses_carry_request_id(client):
    response = client.get("/healthz")
    assert response["X-Request-ID"].startswith("req_")
