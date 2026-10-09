"""Identity API: /api/v1/me and /api/v1/auth/csrf."""

import pytest
from rest_framework.test import APIClient

from kayaka.authorization import permissions as perms
from kayaka.tenancy.tests.conftest import login_as


@pytest.mark.django_db
def test_me_returns_identity_and_memberships(owner_a, tenant_a) -> None:
    client = login_as(owner_a)
    response = client.get("/api/v1/me")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["email"] == "owner@demo.kayaka.local"
    assert data["isAuthenticated"] is True
    assert data["platformRoles"] == []
    assert len(data["memberships"]) == 1
    membership = data["memberships"][0]
    assert membership["tenant"]["slug"] == tenant_a.slug
    assert membership["role"] == "OWNER"
    assert perms.CATALOG_UPDATE in membership["permissions"]


@pytest.mark.django_db
def test_me_platform_admin_exposes_platform_permissions(platform_admin) -> None:
    client = login_as(platform_admin)
    data = client.get("/api/v1/me").json()["data"]
    assert "PLATFORM_ADMIN" in data["platformRoles"]
    assert perms.PLATFORM_TENANTS_VIEW in data["platformPermissions"]
    assert data["memberships"] == []


@pytest.mark.django_db
def test_me_response_has_no_secret_fields(owner_a) -> None:
    client = login_as(owner_a)
    body = client.get("/api/v1/me").text.lower()
    assert "password" not in body
    assert "pbkdf2" not in body
    assert "argon2" not in body


@pytest.mark.django_db
def test_me_requires_authentication() -> None:
    response = APIClient().get("/api/v1/me")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "NOT_AUTHENTICATED"


@pytest.mark.django_db
def test_csrf_endpoint_sets_cookie() -> None:
    client = APIClient()
    response = client.get("/api/v1/auth/csrf")
    assert response.status_code == 200
    assert "kayaka_csrftoken" in client.cookies
