"""Infrastructure probes. Plain Django views: no auth, no DRF, not part of the OpenAPI schema.

- /healthz: the process is up (liveness). Never touches the database.
- /readyz:  the process can serve traffic (readiness). Checks the database.
"""

import logging

from django.db import DatabaseError, connection, transaction
from django.http import HttpRequest, JsonResponse
from django.views.decorators.cache import never_cache

logger = logging.getLogger(__name__)


@never_cache
@transaction.non_atomic_requests
def healthz(request: HttpRequest) -> JsonResponse:
    return JsonResponse({"status": "ok"})


@never_cache
@transaction.non_atomic_requests  # an unreachable DB must yield 503, not fail opening a transaction
def readyz(request: HttpRequest) -> JsonResponse:
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except DatabaseError:
        logger.exception("readiness.database_unavailable")
        return JsonResponse(
            {"status": "unavailable", "checks": {"database": "error"}},
            status=503,
        )
    return JsonResponse({"status": "ok", "checks": {"database": "ok"}})
