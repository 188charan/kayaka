"""Tenancy models: Tenant, Membership, and the tenant-scoped base used by future modules.

A `User` (global identity, in `accounts`) joins a `Tenant` through a `Membership`, which carries
the user's `TenantRole` for that tenant. Row-level security (migration 0002) is anchored on the
`AuditLogEntry` table, which inherits `TenantScopedModel`; later business tables will do the same.
"""

import uuid
from typing import ClassVar

from django.db import models
from django.utils import timezone

from kayaka.authorization.roles import TenantRole


class TenantStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    SUSPENDED = "SUSPENDED", "Suspended"


class MembershipStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    INVITED = "INVITED", "Invited"
    SUSPENDED = "SUSPENDED", "Suspended"


class Tenant(models.Model):
    """A business on the platform. The tenant registry itself is not tenant-scoped data; access
    to it is gated in the application layer (platform roles / membership), not by RLS."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=80, unique=True)
    status = models.CharField(
        max_length=16, choices=TenantStatus.choices, default=TenantStatus.ACTIVE
    )
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tenants"
        ordering: ClassVar = ["name"]

    def __str__(self) -> str:
        return self.name

    @property
    def is_active(self) -> bool:
        return self.status == TenantStatus.ACTIVE


class Membership(models.Model):
    """Links a global user to a tenant with a tenant role. One row per (user, tenant)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="memberships")
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=32, choices=TenantRole.choices)
    status = models.CharField(
        max_length=16, choices=MembershipStatus.choices, default=MembershipStatus.ACTIVE
    )
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "memberships"
        constraints: ClassVar = [
            # A user cannot have two memberships in the same tenant (any status).
            models.UniqueConstraint(
                fields=["user", "tenant"], name="memberships_user_tenant_unique"
            ),
        ]
        indexes: ClassVar = [
            models.Index(fields=["tenant", "user"], name="memberships_tenant_user_idx"),
            models.Index(fields=["status"], name="memberships_status_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.user_id}@{self.tenant_id}:{self.role}"

    @property
    def is_active(self) -> bool:
        return self.status == MembershipStatus.ACTIVE


class TenantScopedModel(models.Model):
    """Abstract base for tenant-owned rows. Carries `tenant` (and thus a `tenant_id` column) that
    row-level security policies key on. Concrete subclasses must enable RLS in a migration via
    `kayaka.tenancy.rls.enable_tenant_rls(...)`."""

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="+")

    class Meta:
        abstract = True


class AuditLogEntry(TenantScopedModel):
    """Minimal tenant-scoped audit record. Phase 2 only establishes the extension point and uses
    this table to prove RLS; a full audit subsystem arrives later. Never store secrets here."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    actor = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    action = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        db_table = "audit_log_entries"
        ordering: ClassVar = ["-created_at"]
        indexes: ClassVar = [
            models.Index(fields=["tenant", "-created_at"], name="audit_tenant_created_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.action}"
