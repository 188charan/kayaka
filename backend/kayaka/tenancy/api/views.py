"""Identity and tenancy endpoints. Authentication itself is handled by django-allauth headless
at /_allauth/browser/v1/*; these endpoints expose identity, tenant access and tenant switching,
all authorization-enforced on the backend."""

from __future__ import annotations

import uuid
from typing import Any, cast

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from kayaka.accounts.models import User
from kayaka.authorization import permissions as perms
from kayaka.authorization.roles import tenant_permissions_for_role
from kayaka.core.api.serializers import ErrorResponseSerializer
from kayaka.tenancy.access import (
    get_active_membership,
    has_permission,
    platform_permissions_for,
    platform_roles_for,
    resolve_authorized_tenant,
    tenant_permissions_for,
)
from kayaka.tenancy.api.base import BaseApiView
from kayaka.tenancy.api.serializers import (
    ActiveTenantResponseSerializer,
    CsrfResponseSerializer,
    MeResponseSerializer,
    PlatformOverviewResponseSerializer,
    TenantDetailResponseSerializer,
    TenantListResponseSerializer,
    TenantSwitchRequestSerializer,
    TenantUpdateSerializer,
)
from kayaka.tenancy.models import Membership, MembershipStatus, Tenant, TenantStatus
from kayaka.tenancy.permissions import platform_permission_required

ACTIVE_TENANT_SESSION_KEY = "active_tenant_id"


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CsrfView(APIView):
    """Sets the CSRF cookie so the SPA can send `X-CSRFToken` on unsafe requests (login, switch)."""

    authentication_classes = ()
    permission_classes = (AllowAny,)

    @extend_schema(
        operation_id="auth_csrf",
        summary="Obtain a CSRF cookie",
        tags=["auth"],
        responses={200: CsrfResponseSerializer},
    )
    def get(self, request: Request) -> Response:
        return Response({"data": {"detail": "ok"}}, headers={"Cache-Control": "no-store"})


class MeView(BaseApiView):
    """Current identity: user, platform roles/permissions, memberships, and active tenant."""

    @extend_schema(
        operation_id="identity_me",
        summary="Get the authenticated identity",
        tags=["identity"],
        responses={200: MeResponseSerializer, "4XX": ErrorResponseSerializer},
    )
    def get(self, request: Request) -> Response:
        user = cast(User, request.user)  # IsAuthenticated guarantees a real user

        active_id = request.session.get(ACTIVE_TENANT_SESSION_KEY)
        active_tenant = None
        if active_id:
            active_tenant = resolve_authorized_tenant(user, active_id)
            if active_tenant is None:  # membership revoked/suspended since switch
                request.session.pop(ACTIVE_TENANT_SESSION_KEY, None)

        memberships = (
            Membership.objects.filter(user=user, status=MembershipStatus.ACTIVE)
            .select_related("tenant")
            .order_by("tenant__name")
        )
        membership_payload = [
            {
                "tenant": {
                    "id": m.tenant.id,
                    "name": m.tenant.name,
                    "slug": m.tenant.slug,
                    "status": m.tenant.status,
                },
                "role": m.role,
                "status": m.status,
                "permissions": sorted(tenant_permissions_for_role(m.role)),
            }
            for m in memberships
        ]

        payload = {
            "data": {
                "id": user.pk,
                "email": getattr(user, "email", ""),
                "fullName": getattr(user, "full_name", ""),
                "isAuthenticated": True,
                "platformRoles": sorted(platform_roles_for(user)),
                "platformPermissions": sorted(platform_permissions_for(user)),
                "activeTenantId": active_tenant.id if active_tenant else None,
                "memberships": membership_payload,
            }
        }
        return Response(payload, headers={"Cache-Control": "no-store"})


class TenantListView(BaseApiView):
    """Tenants the user may see: their memberships, plus all tenants if a platform viewer."""

    @extend_schema(
        operation_id="tenants_list",
        summary="List accessible tenants",
        tags=["tenancy"],
        responses={200: TenantListResponseSerializer, "4XX": ErrorResponseSerializer},
    )
    def get(self, request: Request) -> Response:
        user = cast(User, request.user)  # IsAuthenticated guarantees a real user
        items: dict[uuid.UUID, dict[str, Any]] = {}

        if has_permission(user, perms.PLATFORM_TENANTS_VIEW):
            for tenant in Tenant.objects.all():
                items[tenant.id] = _tenant_summary(tenant, role=None, permissions=[])

        memberships = Membership.objects.filter(
            user=user, status=MembershipStatus.ACTIVE
        ).select_related("tenant")
        for m in memberships:
            items[m.tenant.id] = _tenant_summary(
                m.tenant,
                role=m.role,
                permissions=sorted(tenant_permissions_for(user, m.tenant)),
            )

        data = sorted(items.values(), key=lambda item: str(item["name"]).lower())
        return Response({"data": data}, headers={"Cache-Control": "no-store"})


class TenantDetailView(BaseApiView):
    """Single tenant. Hidden with 404 unless the user is a member or a platform viewer."""

    @extend_schema(
        operation_id="tenants_detail",
        summary="Get a tenant",
        tags=["tenancy"],
        responses={200: TenantDetailResponseSerializer, "4XX": ErrorResponseSerializer},
    )
    def get(self, request: Request, tenant_id: uuid.UUID) -> Response:
        user = request.user
        tenant = resolve_authorized_tenant(user, tenant_id)
        role: str | None = None
        permissions: list[str] = []

        if tenant is not None:
            membership = get_active_membership(user, tenant)
            role = membership.role if membership else None
            permissions = sorted(tenant_permissions_for(user, tenant))
        elif has_permission(user, perms.PLATFORM_TENANTS_VIEW):
            tenant = Tenant.objects.filter(id=tenant_id).first()

        if tenant is None:
            # Do not leak whether the tenant exists.
            raise NotFound()

        return Response(
            {"data": _tenant_summary(tenant, role=role, permissions=permissions)},
            headers={"Cache-Control": "no-store"},
        )

    @extend_schema(
        operation_id="tenants_update",
        summary="Update a tenant",
        tags=["tenancy"],
        request=TenantUpdateSerializer,
        responses={200: TenantDetailResponseSerializer, "4XX": ErrorResponseSerializer},
    )
    def patch(self, request: Request, tenant_id: uuid.UUID) -> Response:
        user = request.user
        # Non-members get 404 (existence hidden) before any permission message is produced.
        tenant = resolve_authorized_tenant(user, tenant_id)
        if tenant is None:
            raise NotFound()
        if not has_permission(user, perms.TENANT_UPDATE, tenant=tenant):
            raise PermissionDenied()

        serializer = TenantUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tenant.name = serializer.validated_data["name"]
        tenant.save(update_fields=["name", "updated_at"])

        permissions = sorted(tenant_permissions_for(user, tenant))
        membership = get_active_membership(user, tenant)
        role = membership.role if membership else None
        return Response(
            {"data": _tenant_summary(tenant, role=role, permissions=permissions)},
            headers={"Cache-Control": "no-store"},
        )


class PlatformOverviewView(BaseApiView):
    """Platform-only overview. Requires a platform permission; tenant members are denied (403)."""

    permission_classes = (IsAuthenticated, platform_permission_required(perms.PLATFORM_HEALTH_VIEW))

    @extend_schema(
        operation_id="platform_overview",
        summary="Platform overview (platform roles only)",
        tags=["platform"],
        responses={200: PlatformOverviewResponseSerializer, "4XX": ErrorResponseSerializer},
    )
    def get(self, request: Request) -> Response:
        total = Tenant.objects.count()
        active = Tenant.objects.filter(status=TenantStatus.ACTIVE).count()
        return Response(
            {"data": {"tenants": total, "activeTenants": active}},
            headers={"Cache-Control": "no-store"},
        )


class TenantSwitchView(BaseApiView):
    """Set the session's active tenant, validated against membership (never trusts the id)."""

    @extend_schema(
        operation_id="tenants_switch",
        summary="Switch the active tenant",
        tags=["tenancy"],
        request=TenantSwitchRequestSerializer,
        responses={200: ActiveTenantResponseSerializer, "4XX": ErrorResponseSerializer},
    )
    def post(self, request: Request) -> Response:
        serializer = TenantSwitchRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tenant_id = serializer.validated_data["tenantId"]

        tenant = resolve_authorized_tenant(request.user, tenant_id)
        if tenant is None:
            raise NotFound()  # no active membership -> hide existence

        request.session[ACTIVE_TENANT_SESSION_KEY] = str(tenant.id)
        return Response(
            {"data": {"activeTenantId": str(tenant.id)}},
            headers={"Cache-Control": "no-store"},
        )


def _tenant_summary(tenant: Tenant, *, role: str | None, permissions: list[str]) -> dict[str, Any]:
    return {
        "id": tenant.id,
        "name": tenant.name,
        "slug": tenant.slug,
        "status": tenant.status,
        "role": role,
        "permissions": permissions,
    }
