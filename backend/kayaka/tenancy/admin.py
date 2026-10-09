"""Django admin for tenancy models. Admin is an ops tool (DJANGO_ADMIN_ENABLED), never the
product's tenant-management UI and never the source of Kayaka RBAC."""

from django.contrib import admin

from kayaka.tenancy.models import AuditLogEntry, Membership, Tenant


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("name", "slug", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("name", "slug")
    ordering = ("name",)


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("user", "tenant", "role", "status", "created_at")
    list_filter = ("role", "status")
    search_fields = ("user__email", "tenant__name", "tenant__slug")
    raw_id_fields = ("user", "tenant")


@admin.register(AuditLogEntry)
class AuditLogEntryAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("tenant", "action", "actor", "created_at")
    list_filter = ("action",)
    search_fields = ("tenant__name", "action")
    raw_id_fields = ("tenant", "actor")
