"""DRF permission classes expressed in permission codes (never role names).

Unauthenticated requests fail ``IsAuthenticated`` and become 401; authenticated-but-unauthorized
requests become 403 (see the error handler). Tenant-scoped checks read ``view.tenant``, which the
view resolved and authorized via membership.
"""

from __future__ import annotations

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from kayaka.tenancy.access import has_permission


def platform_permission_required(code: str) -> type[BasePermission]:
    """Permission class requiring a platform permission code (ignores tenant context)."""

    class _RequirePlatformPermission(BasePermission):
        message = "You don't have permission to do that."

        def has_permission(self, request: Request, view: APIView) -> bool:
            return has_permission(request.user, code)

    return _RequirePlatformPermission


def tenant_permission_required(code: str) -> type[BasePermission]:
    """Permission class requiring a tenant permission code against ``view.tenant``."""

    class _RequireTenantPermission(BasePermission):
        message = "You don't have permission to do that."

        def has_permission(self, request: Request, view: APIView) -> bool:
            tenant = getattr(view, "tenant", None)
            if tenant is None:
                return False
            return has_permission(request.user, code, tenant=tenant)

    return _RequireTenantPermission
