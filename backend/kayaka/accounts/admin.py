"""Django admin registration. Admin is an ops tool, enabled only with DJANGO_ADMIN_ENABLED=true."""

from django.contrib import admin

from kayaka.accounts.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):  # type: ignore[type-arg]  # generic only in stubs
    list_display = ("email", "full_name", "is_active", "is_staff", "date_joined")
    list_filter = ("is_active", "is_staff", "is_superuser")
    search_fields = ("email", "full_name")
    ordering = ("email",)
    # Passwords are never edited here; use `manage.py changepassword`.
    fields = (
        "email",
        "full_name",
        "is_active",
        "is_staff",
        "is_superuser",
        "groups",
        "user_permissions",
        "last_login",
        "date_joined",
    )
    readonly_fields = ("last_login", "date_joined")
    filter_horizontal = ("groups", "user_permissions")
