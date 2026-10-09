"""Roles and their explicit permission-code mappings.

Tenant roles and platform roles are deliberately separate enums with disjoint permission sets
(ADR 0010). A tenant role never grants a `platform.*` code, and a platform role never grants a
tenant code. `is_staff`/`is_superuser` on the Django user are NOT Kayaka roles — they only gate
Django admin access.
"""

from __future__ import annotations

from django.db import models

from kayaka.authorization import permissions as perms


class TenantRole(models.TextChoices):
    OWNER = "OWNER", "Owner"
    MANAGER = "MANAGER", "Manager"
    STAFF = "STAFF", "Staff"
    MARKETING = "MARKETING", "Marketing"


class PlatformRole(models.TextChoices):
    PLATFORM_ADMIN = "PLATFORM_ADMIN", "Platform admin"
    SUPPORT = "SUPPORT", "Support"
    # ANALYST is reserved for a later phase and is intentionally granted no permissions yet.
    ANALYST = "ANALYST", "Analyst"


TENANT_ROLE_PERMISSIONS: dict[str, frozenset[str]] = {
    TenantRole.OWNER: frozenset(
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
    ),
    TenantRole.MANAGER: frozenset(
        {
            perms.TENANT_VIEW,
            perms.CATALOG_VIEW,
            perms.CATALOG_CREATE,
            perms.CATALOG_UPDATE,
            perms.CATALOG_DELETE,
            perms.INQUIRY_VIEW,
            perms.INQUIRY_MANAGE,
            perms.CUSTOMER_VIEW,
            perms.ANALYTICS_VIEW,
            perms.STOREFRONT_VIEW,
            perms.STOREFRONT_EDIT,
        }
    ),
    TenantRole.STAFF: frozenset(
        {
            perms.TENANT_VIEW,
            perms.CATALOG_VIEW,
            perms.CATALOG_UPDATE,
            perms.INQUIRY_VIEW,
            perms.INQUIRY_MANAGE,
            perms.CUSTOMER_VIEW,
        }
    ),
    TenantRole.MARKETING: frozenset(
        {
            perms.TENANT_VIEW,
            perms.STOREFRONT_VIEW,
            perms.STOREFRONT_EDIT,
            perms.STOREFRONT_PUBLISH,
            perms.ANALYTICS_VIEW,
        }
    ),
}

PLATFORM_ROLE_PERMISSIONS: dict[str, frozenset[str]] = {
    PlatformRole.PLATFORM_ADMIN: frozenset(
        {
            perms.PLATFORM_TENANTS_VIEW,
            perms.PLATFORM_TENANTS_MANAGE,
            perms.PLATFORM_AUDIT_VIEW,
            perms.PLATFORM_HEALTH_VIEW,
        }
    ),
    PlatformRole.SUPPORT: frozenset(
        {
            perms.PLATFORM_TENANTS_VIEW,
            perms.PLATFORM_HEALTH_VIEW,
        }
    ),
    PlatformRole.ANALYST: frozenset(),  # reserved; no active permissions yet
}


def tenant_permissions_for_role(role: str) -> frozenset[str]:
    """Permission codes granted by a single tenant role (empty for unknown roles)."""
    return TENANT_ROLE_PERMISSIONS.get(role, frozenset())


def platform_permissions_for_role(role: str) -> frozenset[str]:
    """Permission codes granted by a single platform role (empty for unknown roles)."""
    return PLATFORM_ROLE_PERMISSIONS.get(role, frozenset())


# Sanity invariants, verified by tests: scopes never cross.
def _tenant_roles_grant_only_tenant_codes() -> bool:
    return all(codes <= perms.TENANT_CODES for codes in TENANT_ROLE_PERMISSIONS.values())


def _platform_roles_grant_only_platform_codes() -> bool:
    return all(codes <= perms.PLATFORM_CODES for codes in PLATFORM_ROLE_PERMISSIONS.values())
