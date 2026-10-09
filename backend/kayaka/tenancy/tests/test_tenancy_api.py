"""Tenancy API: list, detail, update, switch, platform overview."""

import pytest

from kayaka.tenancy.tests.conftest import login_as


@pytest.mark.django_db
def test_tenant_list_for_member_shows_their_tenant(owner_a, tenant_a) -> None:
    client = login_as(owner_a)
    data = client.get("/api/v1/tenants").json()["data"]
    assert [t["slug"] for t in data] == [tenant_a.slug]
    assert data[0]["role"] == "OWNER"


@pytest.mark.django_db
def test_tenant_list_for_platform_admin_shows_all(platform_admin, tenant_a, tenant_b) -> None:
    client = login_as(platform_admin)
    data = client.get("/api/v1/tenants").json()["data"]
    slugs = {t["slug"] for t in data}
    assert {tenant_a.slug, tenant_b.slug} <= slugs
    # Platform viewer has no tenant role in these tenants.
    assert all(t["role"] is None for t in data)


@pytest.mark.django_db
def test_tenant_detail_for_member(owner_a, tenant_a) -> None:
    client = login_as(owner_a)
    response = client.get(f"/api/v1/tenants/{tenant_a.id}")
    assert response.status_code == 200
    assert response.json()["data"]["slug"] == tenant_a.slug


@pytest.mark.django_db
def test_owner_can_update_own_tenant(owner_a, tenant_a) -> None:
    client = login_as(owner_a)
    response = client.patch(
        f"/api/v1/tenants/{tenant_a.id}", {"name": "Anjali Renamed"}, format="json"
    )
    assert response.status_code == 200
    tenant_a.refresh_from_db()
    assert tenant_a.name == "Anjali Renamed"


@pytest.mark.django_db
def test_switch_sets_active_tenant(owner_a, tenant_a) -> None:
    client = login_as(owner_a)
    response = client.post("/api/v1/tenants/switch", {"tenantId": str(tenant_a.id)}, format="json")
    assert response.status_code == 200
    assert response.json()["data"]["activeTenantId"] == str(tenant_a.id)
    # Reflected by /me.
    me = client.get("/api/v1/me").json()["data"]
    assert me["activeTenantId"] == str(tenant_a.id)


@pytest.mark.django_db
def test_platform_overview_for_platform_admin(platform_admin, tenant_a, tenant_b) -> None:
    client = login_as(platform_admin)
    response = client.get("/api/v1/platform/overview")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["tenants"] >= 2
    assert data["activeTenants"] >= 2
