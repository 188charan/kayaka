from django.conf import settings
from django.urls import URLPattern, URLResolver, include, path

from kayaka.core import health

urlpatterns: list[URLPattern | URLResolver] = [
    path("healthz", health.healthz, name="healthz"),
    path("readyz", health.readyz, name="readyz"),
    path("api/v1/", include("config.api_v1")),
    # django-allauth headless browser endpoints (session-based): /_allauth/browser/v1/*.
    # The Next.js same-origin proxy forwards these alongside /api/v1/* (ADR 0011).
    path("_allauth/", include("allauth.headless.urls")),
]

if settings.ADMIN_ENABLED:
    from django.contrib import admin

    urlpatterns.append(path(settings.ADMIN_URL, admin.site.urls))

# Unknown URLs and unhandled errors outside DRF views still return the JSON error envelope.
handler400 = "kayaka.core.api.errors.bad_request"
handler403 = "kayaka.core.api.errors.permission_denied"
handler404 = "kayaka.core.api.errors.not_found"
handler500 = "kayaka.core.api.errors.server_error"
