"""Permission codes — the stable vocabulary authorization is expressed in.

Authorization is checked against these codes, never against role names directly (a view asks
"may this user do `catalog.update`?", not "is this user an OWNER?"). Roles map to sets of these
codes in `roles.py`. Frontends may read a user's effective codes to shape UX, but the backend
is always the authority.

Only codes relevant to the current and near-future architecture are defined. Business modules
(catalog, inquiry, customer, storefront, analytics) are not implemented until later phases;
their codes are declared here so roles can be mapped coherently now, but no endpoint enforces
them yet.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class PermissionScope(StrEnum):
    """Where a permission applies. Tenant and platform scopes never mix (ADR 0010)."""

    TENANT = "tenant"
    PLATFORM = "platform"


@dataclass(frozen=True, slots=True)
class Permission:
    code: str
    name: str
    description: str
    scope: PermissionScope


# ---------------------------------------------------------------- tenant-scoped codes
TENANT_VIEW = "tenant.view"
TENANT_UPDATE = "tenant.update"
TENANT_MANAGE_MEMBERS = "tenant.manage_members"
TENANT_MANAGE_SETTINGS = "tenant.manage_settings"

CATALOG_VIEW = "catalog.view"
CATALOG_CREATE = "catalog.create"
CATALOG_UPDATE = "catalog.update"
CATALOG_DELETE = "catalog.delete"

INQUIRY_VIEW = "inquiry.view"
INQUIRY_MANAGE = "inquiry.manage"

CUSTOMER_VIEW = "customer.view"

STOREFRONT_VIEW = "storefront.view"
STOREFRONT_EDIT = "storefront.edit"
STOREFRONT_PUBLISH = "storefront.publish"

ANALYTICS_VIEW = "analytics.view"

# ---------------------------------------------------------------- platform-scoped codes
PLATFORM_TENANTS_VIEW = "platform.tenants.view"
PLATFORM_TENANTS_MANAGE = "platform.tenants.manage"
PLATFORM_AUDIT_VIEW = "platform.audit.view"
PLATFORM_HEALTH_VIEW = "platform.health.view"


PERMISSIONS: tuple[Permission, ...] = (
    Permission(
        TENANT_VIEW, "View tenant", "View the tenant profile and overview.", PermissionScope.TENANT
    ),
    Permission(TENANT_UPDATE, "Update tenant", "Edit the tenant profile.", PermissionScope.TENANT),
    Permission(
        TENANT_MANAGE_MEMBERS,
        "Manage members",
        "Invite, update and remove tenant members.",
        PermissionScope.TENANT,
    ),
    Permission(
        TENANT_MANAGE_SETTINGS,
        "Manage settings",
        "Change tenant settings and configuration (incl. WhatsApp).",
        PermissionScope.TENANT,
    ),
    Permission(
        CATALOG_VIEW, "View catalog", "View products and categories.", PermissionScope.TENANT
    ),
    Permission(
        CATALOG_CREATE, "Create catalog", "Create products and categories.", PermissionScope.TENANT
    ),
    Permission(
        CATALOG_UPDATE, "Update catalog", "Edit products and categories.", PermissionScope.TENANT
    ),
    Permission(
        CATALOG_DELETE, "Delete catalog", "Delete products and categories.", PermissionScope.TENANT
    ),
    Permission(INQUIRY_VIEW, "View inquiries", "View customer inquiries.", PermissionScope.TENANT),
    Permission(
        INQUIRY_MANAGE,
        "Manage inquiries",
        "Respond to and manage inquiries.",
        PermissionScope.TENANT,
    ),
    Permission(CUSTOMER_VIEW, "View customers", "View customer records.", PermissionScope.TENANT),
    Permission(
        STOREFRONT_VIEW, "View storefront", "View storefront configuration.", PermissionScope.TENANT
    ),
    Permission(
        STOREFRONT_EDIT,
        "Edit storefront",
        "Edit storefront content and theme.",
        PermissionScope.TENANT,
    ),
    Permission(
        STOREFRONT_PUBLISH,
        "Publish storefront",
        "Publish storefront changes.",
        PermissionScope.TENANT,
    ),
    Permission(
        ANALYTICS_VIEW,
        "View analytics",
        "View tenant insights and analytics.",
        PermissionScope.TENANT,
    ),
    Permission(
        PLATFORM_TENANTS_VIEW,
        "View tenants (platform)",
        "View tenants across the platform.",
        PermissionScope.PLATFORM,
    ),
    Permission(
        PLATFORM_TENANTS_MANAGE,
        "Manage tenants (platform)",
        "Create, suspend and reactivate tenants.",
        PermissionScope.PLATFORM,
    ),
    Permission(
        PLATFORM_AUDIT_VIEW,
        "View audit log (platform)",
        "View the platform audit log.",
        PermissionScope.PLATFORM,
    ),
    Permission(
        PLATFORM_HEALTH_VIEW,
        "View health (platform)",
        "View platform health and metrics.",
        PermissionScope.PLATFORM,
    ),
)

PERMISSIONS_BY_CODE: dict[str, Permission] = {perm.code: perm for perm in PERMISSIONS}

ALL_CODES: frozenset[str] = frozenset(PERMISSIONS_BY_CODE)
TENANT_CODES: frozenset[str] = frozenset(
    perm.code for perm in PERMISSIONS if perm.scope is PermissionScope.TENANT
)
PLATFORM_CODES: frozenset[str] = frozenset(
    perm.code for perm in PERMISSIONS if perm.scope is PermissionScope.PLATFORM
)


def is_platform_code(code: str) -> bool:
    return code in PLATFORM_CODES


def is_tenant_code(code: str) -> bool:
    return code in TENANT_CODES
