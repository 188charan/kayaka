from datetime import datetime

import pytest

PING_URL = "/api/v1/public/ping"


@pytest.fixture
def api(client):
    return client


def test_ping_returns_data_envelope(api):
    response = api.get(PING_URL)
    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"data"}
    data = body["data"]
    assert data["service"] == "kayaka-api"
    assert data["version"] == "test"
    assert data["environment"] == "test"
    assert datetime.fromisoformat(data["time"]).tzinfo is not None


def test_ping_is_not_cacheable(api):
    assert api.get(PING_URL)["Cache-Control"] == "no-store"


def test_ping_sets_security_headers(api):
    response = api.get(PING_URL)
    assert response["Content-Security-Policy"] == "default-src 'none'; frame-ancestors 'none'"
    assert response["X-Frame-Options"] == "DENY"
    assert response["X-Content-Type-Options"] == "nosniff"
    assert response["Referrer-Policy"] == "strict-origin-when-cross-origin"


def test_ping_does_not_need_a_database(api):
    # No django_db mark: public ping must not touch the DB (no session lookup).
    assert api.get(PING_URL).status_code == 200


def test_ping_rejects_other_methods_with_error_envelope(api):
    response = api.post(PING_URL, data={}, content_type="application/json")
    assert response.status_code == 405
    assert response.json()["error"]["code"] == "METHOD_NOT_ALLOWED"
