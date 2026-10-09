"""CSRF protection for session-authenticated unsafe requests (master prompt §3).

The clients here use ``enforce_csrf_checks=True`` so DRF's SessionAuthentication actually runs the
CSRF check (the default test client disables it).
"""

import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_unsafe_request_without_csrf_is_rejected(owner_a, tenant_a) -> None:
    client = APIClient(enforce_csrf_checks=True)
    # Authenticated via session, but no CSRF token supplied.
    client.force_login(owner_a, backend="django.contrib.auth.backends.ModelBackend")
    response = client.post("/api/v1/tenants/switch", {"tenantId": str(tenant_a.id)}, format="json")
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "CSRF_FAILED"


@pytest.mark.django_db
def test_unsafe_request_with_valid_csrf_is_accepted(owner_a, tenant_a) -> None:
    client = APIClient(enforce_csrf_checks=True)
    client.force_login(owner_a, backend="django.contrib.auth.backends.ModelBackend")
    client.get("/api/v1/auth/csrf")
    token = client.cookies["kayaka_csrftoken"].value
    response = client.post(
        "/api/v1/tenants/switch",
        {"tenantId": str(tenant_a.id)},
        format="json",
        HTTP_X_CSRFTOKEN=token,
    )
    assert response.status_code == 200


@pytest.mark.django_db
def test_safe_request_needs_no_csrf(owner_a) -> None:
    client = APIClient(enforce_csrf_checks=True)
    client.force_login(owner_a, backend="django.contrib.auth.backends.ModelBackend")
    assert client.get("/api/v1/me").status_code == 200
