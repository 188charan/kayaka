"""Cross-tenant isolation and RBAC boundary suite (Phase 2 master prompt §16).

Each test is numbered to match the required cases. The answer to "Can Tenant A access Tenant B?"
is NO, enforced here at the authorization and service layers; RLS adds the database layer in
test_rls.py.
"""

import pytest

from kayaka.tenancy.tests.conftest import login_as


@pytest.mark.django_db
def test_1_member_can_access_own_tenant(owner_a, tenant_a) -> None:
    client = login_as(owner_a)
    assert client.get(f"/api/v1/tenants/{tenant_a.id}").status_code == 200


@pytest.mark.django_db
def test_2_member_cannot_access_other_tenant(owner_a, tenant_b) -> None:
    client = login_as(owner_a)
    # 404 (not 403) so the existence of tenant B is not leaked.
    assert client.get(f"/api/v1/tenants/{tenant_b.id}").status_code == 404


@pytest.mark.django_db
def test_3_member_cannot_modify_other_tenant(owner_a, tenant_b) -> None:
    client = login_as(owner_a)
    response = client.patch(f"/api/v1/tenants/{tenant_b.id}", {"name": "Hijacked"}, format="json")
    assert response.status_code == 404
    tenant_b.refresh_from_db()
    assert tenant_b.name != "Hijacked"


@pytest.mark.django_db
def test_4_changing_tenant_id_does_not_bypass_membership(owner_a, tenant_b) -> None:
    client = login_as(owner_a)
    # Attempt to switch the active tenant to one the user has no membership in.
    response = client.post("/api/v1/tenants/switch", {"tenantId": str(tenant_b.id)}, format="json")
    assert response.status_code == 404
    me = client.get("/api/v1/me").json()["data"]
    assert me["activeTenantId"] is None


# TEST 5 (RLS blocks cross-tenant rows) and TEST 6 (no context leak) live in test_rls.py.


@pytest.mark.django_db
def test_7_unauthenticated_cannot_access_tenant_apis() -> None:
    from rest_framework.test import APIClient

    client = APIClient()
    assert client.get("/api/v1/me").status_code == 401
    assert client.get("/api/v1/tenants").status_code == 401


@pytest.mark.django_db
def test_8_tenant_user_cannot_access_platform_api(owner_a) -> None:
    client = login_as(owner_a)
    assert client.get("/api/v1/platform/overview").status_code == 403


@pytest.mark.django_db
def test_9_staff_cannot_perform_owner_only_operation(staff_a, tenant_a) -> None:
    client = login_as(staff_a)
    response = client.patch(f"/api/v1/tenants/{tenant_a.id}", {"name": "Staff Edit"}, format="json")
    # Staff is a member (not 404) but lacks tenant.update (403).
    assert response.status_code == 403
    tenant_a.refresh_from_db()
    assert tenant_a.name != "Staff Edit"


@pytest.mark.django_db
def test_10_manager_cannot_perform_platform_administration(manager_a) -> None:
    client = login_as(manager_a)
    assert client.get("/api/v1/platform/overview").status_code == 403


@pytest.mark.django_db
def test_11_multi_tenant_user_can_switch_between_their_tenants(
    multi_user, tenant_a, tenant_b
) -> None:
    client = login_as(multi_user)
    first = client.post("/api/v1/tenants/switch", {"tenantId": str(tenant_a.id)}, format="json")
    assert first.status_code == 200
    assert first.json()["data"]["activeTenantId"] == str(tenant_a.id)

    second = client.post("/api/v1/tenants/switch", {"tenantId": str(tenant_b.id)}, format="json")
    assert second.status_code == 200
    assert second.json()["data"]["activeTenantId"] == str(tenant_b.id)


@pytest.mark.django_db
def test_12_user_cannot_reach_tenant_without_membership(multi_user, tenant_c) -> None:
    client = login_as(multi_user)
    assert client.get(f"/api/v1/tenants/{tenant_c.id}").status_code == 404
    switch = client.post("/api/v1/tenants/switch", {"tenantId": str(tenant_c.id)}, format="json")
    assert switch.status_code == 404
