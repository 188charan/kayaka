"""RBAC mapping and membership-aware authorization checks."""

import pytest

from kayaka.authorization import permissions as perms
from kayaka.authorization.roles import (
    PlatformRole,
    TenantRole,
    _platform_roles_grant_only_platform_codes,
    _tenant_roles_grant_only_tenant_codes,
    platform_permissions_for_role,
    tenant_permissions_for_role,
)
from kayaka.tenancy.access import (
    has_permission,
    platform_permissions_for,
    tenant_permissions_for,
)
from kayaka.tenancy.models import MembershipStatus, TenantStatus


def test_scopes_never_cross() -> None:
    assert _tenant_roles_grant_only_tenant_codes()
    assert _platform_roles_grant_only_platform_codes()


def test_owner_permission_set() -> None:
    assert tenant_permissions_for_role(TenantRole.OWNER) == frozenset(
        {
            perms.TENANT_VIEW,
            perms.TENANT_UPDATE,
            perms.TENANT_MANAGE_MEMBERS,
            perms.TENANT_MANAGE_SETTINGS,
            perms.CATALOG_VIEW,
            perms.CATALOG_CREATE,
            perms.CATALOG_UPDATE,
            perms.CATALOG_DELETE,
            perms.STOREFRONT_VIEW,
            perms.STOREFRONT_EDIT,
            perms.STOREFRONT_PUBLISH,
            perms.INQUIRY_VIEW,
            perms.INQUIRY_MANAGE,
            perms.CUSTOMER_VIEW,
            perms.ANALYTICS_VIEW,
        }
    )


def test_staff_cannot_update_tenant_or_delete_catalog() -> None:
    staff = tenant_permissions_for_role(TenantRole.STAFF)
    assert perms.CATALOG_VIEW in staff
    assert perms.TENANT_UPDATE not in staff
    assert perms.CATALOG_DELETE not in staff
    assert perms.TENANT_MANAGE_MEMBERS not in staff


def test_marketing_scope() -> None:
    marketing = tenant_permissions_for_role(TenantRole.MARKETING)
    assert marketing == frozenset(
        {
            perms.TENANT_VIEW,
            perms.STOREFRONT_VIEW,
            perms.STOREFRONT_EDIT,
            perms.STOREFRONT_PUBLISH,
            perms.ANALYTICS_VIEW,
        }
    )
    assert perms.CATALOG_CREATE not in marketing


def test_platform_admin_and_support_sets() -> None:
    assert platform_permissions_for_role(PlatformRole.PLATFORM_ADMIN) == frozenset(
        {
            perms.PLATFORM_TENANTS_VIEW,
            perms.PLATFORM_TENANTS_MANAGE,
            perms.PLATFORM_AUDIT_VIEW,
            perms.PLATFORM_HEALTH_VIEW,
        }
    )
    assert platform_permissions_for_role(PlatformRole.SUPPORT) == frozenset(
        {perms.PLATFORM_TENANTS_VIEW, perms.PLATFORM_HEALTH_VIEW}
    )


def test_analyst_has_no_permissions_yet() -> None:
    assert platform_permissions_for_role(PlatformRole.ANALYST) == frozenset()


@pytest.mark.django_db
def test_has_permission_tenant_scope(owner_a, staff_a, tenant_a, tenant_b) -> None:
    assert has_permission(owner_a, perms.CATALOG_UPDATE, tenant=tenant_a)
    # Owner of A has no permission in B (no membership there).
    assert not has_permission(owner_a, perms.CATALOG_UPDATE, tenant=tenant_b)
    # Staff cannot update the tenant.
    assert not has_permission(staff_a, perms.TENANT_UPDATE, tenant=tenant_a)


@pytest.mark.django_db
def test_tenant_role_never_grants_platform_codes(owner_a) -> None:
    assert not has_permission(owner_a, perms.PLATFORM_TENANTS_VIEW)
    assert platform_permissions_for(owner_a) == frozenset()


@pytest.mark.django_db
def test_platform_role_never_grants_tenant_codes(platform_admin, tenant_a) -> None:
    assert has_permission(platform_admin, perms.PLATFORM_TENANTS_VIEW)
    assert not has_permission(platform_admin, perms.CATALOG_UPDATE, tenant=tenant_a)


@pytest.mark.django_db
def test_suspended_tenant_grants_nothing(owner_a, tenant_a) -> None:
    tenant_a.status = TenantStatus.SUSPENDED
    tenant_a.save(update_fields=["status"])
    assert tenant_permissions_for(owner_a, tenant_a) == frozenset()


@pytest.mark.django_db
def test_suspended_membership_grants_nothing(make_user, add_member, tenant_a) -> None:
    user = make_user("suspended@demo.kayaka.local")
    add_member(user, tenant_a, TenantRole.OWNER, status=MembershipStatus.SUSPENDED)
    assert tenant_permissions_for(user, tenant_a) == frozenset()
