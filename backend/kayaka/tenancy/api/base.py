"""Base DRF view that establishes transaction-local DB context for every authenticated request.

After DRF authenticates and authorizes the request, the view drops the connection to the
unprivileged ``kayaka_app`` role and sets the ``kayaka.user_id`` GUC (and ``kayaka.tenant_id``
when a tenant has been resolved and authorized). Because it runs inside the ATOMIC_REQUESTS
transaction and uses ``SET LOCAL``, the context resets when the request's transaction ends.
"""

from __future__ import annotations

from typing import Any

from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.request import Request
from rest_framework.views import APIView

from kayaka.tenancy.db import apply_tenant_context
from kayaka.tenancy.models import Tenant


class BaseApiView(APIView):
    """Authenticated API view. Subclasses may set ``self.tenant`` in ``resolve_tenant`` to also
    pin the tenant GUC for row-level security."""

    permission_classes: tuple[type[BasePermission], ...] = (IsAuthenticated,)
    tenant: Tenant | None = None

    def resolve_tenant(self, request: Request, **kwargs: Any) -> Tenant | None:
        """Override to resolve + authorize a tenant for tenant-scoped endpoints. Returns None by
        default (identity/platform endpoints are not tenant-scoped)."""
        return None

    def initial(self, request: Request, *args: Any, **kwargs: Any) -> None:
        super().initial(request, *args, **kwargs)
        # Runs after authentication + permission checks, inside the request transaction.
        self.tenant = self.resolve_tenant(request, **kwargs)
        user = request.user
        user_id = user.pk if getattr(user, "is_authenticated", False) else None
        apply_tenant_context(
            tenant_id=self.tenant.id if self.tenant is not None else None,
            user_id=user_id,
        )
