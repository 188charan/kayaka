"""Response shapes shared by every endpoint, declared so they appear in the OpenAPI schema
and therefore in the generated TypeScript types."""

from typing import TYPE_CHECKING, Any

from rest_framework import serializers

# DRF's Serializer is generic only in the type stubs, not at runtime.
if TYPE_CHECKING:
    Serializer = serializers.Serializer[Any]
else:
    Serializer = serializers.Serializer


class ErrorDetailSerializer(Serializer):
    field = serializers.CharField(allow_null=True)
    code = serializers.CharField()
    message = serializers.CharField()


class ErrorBodySerializer(Serializer):
    code = serializers.CharField(help_text="Stable machine-readable code, e.g. VALIDATION_ERROR")
    message = serializers.CharField(help_text="Human-readable message, safe to show to users")
    details = ErrorDetailSerializer(many=True, required=False)
    requestId = serializers.CharField(allow_null=True)  # wire format is camelCase


class ErrorResponseSerializer(Serializer):
    error = ErrorBodySerializer()


class PingSerializer(Serializer):
    service = serializers.CharField()
    version = serializers.CharField()
    environment = serializers.CharField()
    time = serializers.DateTimeField()


class PingResponseSerializer(Serializer):
    # A field named `data` is fine at runtime (DRF's metaclass moves declared fields off the
    # class), but the stubs see it shadowing Serializer.data.
    data = PingSerializer()  # type: ignore[assignment]
