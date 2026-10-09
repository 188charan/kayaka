"""Membership-aware authorization — the single place that answers "may this user do X?".

Views never check role names. They call :func:`has_permission` (or the DRF permission classes in
``permissions.py``) with a permission code. Platform codes are resolved from the user's
``PlatformRoleAssignment`` rows; tenant codes require an active membership in an active tenant.
Scopes never cross: a tenant membership can never satisfy a ``platform.*`` code and vice versa.
"""

from __future__ import annotations

import uuid

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AnonymousUser

from kayaka.accounts.models import User
from kayaka.authorization import permissions as perms
from kayaka.authorization.roles import platform_permissions_for_role, tenant_permissions_for_role
from kayaka.tenancy.models import Membership, MembershipStatus, Tenant, TenantStatus

UserLike = AbstractBaseUser | AnonymousUser


def _authenticated(user: UserLike) -> User | None:
    return user if isinstance(user, User) and user.is_authenticated else None


def get_active_membership(user: UserLike, tenant: Tenant) -> Membership | None:
    account = _authenticated(user)
    if account is None:
        return None
    return (
        Membership.objects.filter(user=account, tenant=tenant, status=MembershipStatus.ACTIVE)
        .select_related("tenant")
        .first()
    )


def tenant_permissions_for(user: UserLike, tenant: Tenant) -> frozenset[str]:
    """Effective tenant permission codes for ``user`` in ``tenant`` (empty if no active access)."""
    if tenant.status != TenantStatus.ACTIVE:
        return frozenset()
    membership = get_active_membership(user, tenant)
    if membership is None:
        return frozenset()
    return tenant_permissions_for_role(membership.role)


def platform_roles_for(user: UserLike) -> list[str]:
    account = _authenticated(user)
    if account is None:
        return []
    return list(account.platform_roles.values_list("role", flat=True))


def platform_permissions_for(user: UserLike) -> frozenset[str]:
    """Union of permission codes granted by all of the user's platform roles."""
    codes: set[str] = set()
    for role in platform_roles_for(user):
        codes |= platform_permissions_for_role(role)
    return frozenset(codes)


def has_permission(user: UserLike, code: str, *, tenant: Tenant | None = None) -> bool:
    """Authoritative check. Platform codes ignore ``tenant``; tenant codes require one."""
    if _authenticated(user) is None:
        return False
    if perms.is_platform_code(code):
        return code in platform_permissions_for(user)
    if perms.is_tenant_code(code):
        if tenant is None:
            return False
        return code in tenant_permissions_for(user, tenant)
    return False  # unknown code: deny


def resolve_authorized_tenant(user: UserLike, tenant_id: uuid.UUID | str) -> Tenant | None:
    """Return the tenant only if the user has an active membership in it; otherwise None.

    This is the chokepoint that stops a user reaching a tenant by guessing/changing an id, slug,
    header or query param: no membership -> no tenant, regardless of what was requested.
    """
    account = _authenticated(user)
    if account is None:
        return None
    membership = (
        Membership.objects.filter(user=account, tenant_id=tenant_id, status=MembershipStatus.ACTIVE)
        .select_related("tenant")
        .first()
    )
    return membership.tenant if membership is not None else None
