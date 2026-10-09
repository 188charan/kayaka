"""OpenAPI shapes for the identity and tenancy endpoints (camelCase on the wire)."""

from typing import TYPE_CHECKING, Any

from rest_framework import serializers

if TYPE_CHECKING:
    Serializer = serializers.Serializer[Any]
else:
    Serializer = serializers.Serializer


class TenantSerializer(Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    slug = serializers.CharField()
    status = serializers.CharField()


class MembershipSerializer(Serializer):
    tenant = TenantSerializer()
    role = serializers.CharField()
    status = serializers.CharField()
    permissions = serializers.ListField(child=serializers.CharField())


class MeSerializer(Serializer):
    id = serializers.UUIDField()
    email = serializers.EmailField()
    fullName = serializers.CharField(allow_blank=True)
    isAuthenticated = serializers.BooleanField()
    platformRoles = serializers.ListField(child=serializers.CharField())
    platformPermissions = serializers.ListField(child=serializers.CharField())
    activeTenantId = serializers.UUIDField(allow_null=True)
    memberships = MembershipSerializer(many=True)


class MeResponseSerializer(Serializer):
    data = MeSerializer()  # type: ignore[assignment]


class TenantSummarySerializer(Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    slug = serializers.CharField()
    status = serializers.CharField()
    role = serializers.CharField(allow_null=True)
    permissions = serializers.ListField(child=serializers.CharField())


class TenantListResponseSerializer(Serializer):
    data = TenantSummarySerializer(many=True)  # type: ignore[assignment]


class TenantDetailResponseSerializer(Serializer):
    data = TenantSummarySerializer()  # type: ignore[assignment]


class TenantUpdateSerializer(Serializer):
    name = serializers.CharField(max_length=200)


class TenantSwitchRequestSerializer(Serializer):
    tenantId = serializers.UUIDField()


class PlatformOverviewSerializer(Serializer):
    tenants = serializers.IntegerField()
    activeTenants = serializers.IntegerField()


class PlatformOverviewResponseSerializer(Serializer):
    data = PlatformOverviewSerializer()  # type: ignore[assignment]


class ActiveTenantSerializer(Serializer):
    activeTenantId = serializers.UUIDField(allow_null=True)


class ActiveTenantResponseSerializer(Serializer):
    data = ActiveTenantSerializer()  # type: ignore[assignment]


class CsrfSerializer(Serializer):
    detail = serializers.CharField()


class CsrfResponseSerializer(Serializer):
    data = CsrfSerializer()  # type: ignore[assignment]
