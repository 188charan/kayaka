import uuid
from typing import Any, ClassVar

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.db.models.functions import Lower
from django.utils import timezone

from kayaka.accounts.managers import UserManager, normalize_email
from kayaka.authorization.roles import PlatformRole


class User(AbstractBaseUser, PermissionsMixin):
    """A person who can sign in: platform staff or a tenant member (customers have no login in MVP).

    Identity is global; a user can belong to several tenants through memberships (Phase 2).
    `is_staff` only grants Django admin access (an ops tool). Platform and tenant
    permissions come from the RBAC tables added in Phase 2, never from these flags.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    # Stored lowercase (see save()). `unique` serves lookups; the Lower() constraint below also
    # rejects case variants written by code paths that bypass save() (bulk_create, update()).
    email = models.EmailField(max_length=254, unique=True)
    full_name = models.CharField(max_length=150, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects: ClassVar[UserManager] = UserManager()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS: ClassVar[list[str]] = []

    class Meta:
        db_table = "users"
        constraints: ClassVar = [
            models.UniqueConstraint(Lower("email"), name="users_email_ci_unique"),
        ]

    def __str__(self) -> str:
        return self.email

    def clean(self) -> None:
        super().clean()
        self.email = normalize_email(self.email)

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.email = normalize_email(self.email)
        super().save(*args, **kwargs)


class PlatformRoleAssignment(models.Model):
    """A platform-scoped role granted to a global user (PLATFORM_ADMIN, SUPPORT, ...).

    Platform roles are explicit and separate from tenant memberships and from Django's
    `is_staff`/`is_superuser` flags. A user may hold more than one platform role; the effective
    platform permissions are the union of their roles' permission codes.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="platform_roles",
    )
    role = models.CharField(max_length=32, choices=PlatformRole.choices)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        db_table = "platform_role_assignments"
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["user", "role"], name="platform_role_unique_per_user"),
        ]

    def __str__(self) -> str:
        return f"{self.user_id}:{self.role}"
