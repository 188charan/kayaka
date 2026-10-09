"""All routes under /api/v1/, grouped by surface (see docs/development/api-conventions.md)."""

from django.conf import settings
from django.urls import URLPattern, URLResolver, path, re_path

from kayaka.core.api.errors import api_not_found
from kayaka.core.api.views import ping_view
from kayaka.tenancy.api import urls as tenancy_urls

app_name = "api_v1"

public_patterns: list[URLPattern | URLResolver] = [
    path("public/ping", ping_view, name="public-ping"),
]

# Identity + tenancy (authenticated): /me, /tenants, /tenants/switch, /tenants/{id}, /auth/csrf.
urlpatterns: list[URLPattern | URLResolver] = [*public_patterns, *tenancy_urls.urlpatterns]

if settings.DEBUG:
    from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

    urlpatterns += [
        path("schema", SpectacularAPIView.as_view(), name="schema"),
        path("docs", SpectacularSwaggerView.as_view(url_name="api_v1:schema"), name="docs"),
    ]

# Must stay last: unknown API URLs return the JSON error envelope.
urlpatterns.append(re_path(r"^.*$", api_not_found, name="not-found"))
