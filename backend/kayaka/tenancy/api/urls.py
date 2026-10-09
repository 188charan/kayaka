"""URL patterns for identity + tenancy, mounted under /api/v1/ by config.api_v1."""

from django.urls import URLPattern, URLResolver, path

from kayaka.tenancy.api import views

urlpatterns: list[URLPattern | URLResolver] = [
    path("auth/csrf", views.CsrfView.as_view(), name="auth-csrf"),
    path("me", views.MeView.as_view(), name="identity-me"),
    path("tenants", views.TenantListView.as_view(), name="tenants-list"),
    path("tenants/switch", views.TenantSwitchView.as_view(), name="tenants-switch"),
    path("tenants/<uuid:tenant_id>", views.TenantDetailView.as_view(), name="tenants-detail"),
    path("platform/overview", views.PlatformOverviewView.as_view(), name="platform-overview"),
]
