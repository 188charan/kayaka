from django.conf import settings
from django.db import transaction
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from kayaka.core.api.serializers import ErrorResponseSerializer, PingResponseSerializer


class PingView(APIView):
    """Public liveness check for the API surface. Used by the frontend walking skeleton."""

    authentication_classes = ()  # public: no session, so no CSRF and no DB session lookup
    permission_classes = (AllowAny,)

    @extend_schema(
        operation_id="public_ping",
        summary="Ping the public API",
        tags=["public"],
        responses={200: PingResponseSerializer, "4XX": ErrorResponseSerializer},
    )
    def get(self, request: Request) -> Response:
        payload = {
            "data": {
                "service": "kayaka-api",
                "version": settings.APP_VERSION,
                "environment": settings.APP_ENV,
                "time": timezone.now(),
            }
        }
        return Response(payload, headers={"Cache-Control": "no-store"})


# ATOMIC_REQUESTS would open a DB transaction for every view; ping must answer without the DB.
ping_view = transaction.non_atomic_requests(PingView.as_view())
