"""Idempotent local-dev seed for the canonical demo personas (see docs/development/).

Passwords are NEVER hard-coded. Supply one via --password or the KAYAKA_DEMO_PASSWORD env var:

    KAYAKA_DEMO_PASSWORD=change-me-locally python manage.py seed_demo_data

Running it again updates tenants/memberships without creating duplicates and WITHOUT resetting
existing users' passwords (pass --reset-passwords to force that). The command refuses to run
outside a development/test environment unless --force is given. These are development personas
only; never run against staging or production. The supplied password is never printed or logged.
"""

from __future__ import annotations

import os
from collections.abc import Sequence
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError, CommandParser
from django.db import transaction

from kayaka.accounts.models import PlatformRoleAssignment, User
from kayaka.authorization.roles import PlatformRole, TenantRole
from kayaka.tenancy.models import Membership, MembershipStatus, Tenant, TenantStatus

PLATFORM_ADMIN_EMAIL = "admin@kayaka.local"

ANJALI = {"name": "Anjali Jewellery & Décor", "slug": "anjali-jewellery"}
NAMMA = {"name": "Namma Crafts", "slug": "namma-crafts"}

ANJALI_MEMBERS = [
    ("owner@demo.kayaka.local", "Anjali", TenantRole.OWNER),
    ("manager@demo.kayaka.local", "Rahul", TenantRole.MANAGER),
    ("staff@demo.kayaka.local", "Sneha", TenantRole.STAFF),
    ("marketing@demo.kayaka.local", "Karthik", TenantRole.MARKETING),
]
NAMMA_MEMBERS = [
    ("owner@namma.kayaka.local", "Namma Owner", TenantRole.OWNER),
]

# Environments this command is allowed to touch (APP_ENV). Anything else requires --force.
ALLOWED_ENVIRONMENTS = {"development", "test", "local"}


class Command(BaseCommand):
    help = "Create/update the canonical demo users, tenants and memberships (idempotent)."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--password",
            dest="password",
            default=None,
            help="Demo password. Falls back to the KAYAKA_DEMO_PASSWORD env var.",
        )
        parser.add_argument(
            "--reset-passwords",
            action="store_true",
            dest="reset_passwords",
            help="Reset passwords on EXISTING demo users (default: only set on creation).",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            dest="force",
            help="Allow running outside a development/test environment.",
        )

    @transaction.atomic
    def handle(self, *args: Any, **options: Any) -> None:
        self._guard_environment(force=options["force"])

        password = options.get("password") or os.environ.get("KAYAKA_DEMO_PASSWORD")
        if not password:
            raise CommandError(
                "No demo password provided. Pass --password or set KAYAKA_DEMO_PASSWORD. "
                "Passwords are never stored in source."
            )
        reset = options["reset_passwords"]

        admin, created = self._upsert_user(
            PLATFORM_ADMIN_EMAIL, "Charan", password, reset=reset, is_staff=True
        )
        PlatformRoleAssignment.objects.get_or_create(user=admin, role=PlatformRole.PLATFORM_ADMIN)
        state = self._state(created, reset)
        self.stdout.write(f"platform admin: {admin.email} [PLATFORM_ADMIN] ({state})")

        self._seed_tenant(ANJALI, ANJALI_MEMBERS, password, reset=reset)
        self._seed_tenant(NAMMA, NAMMA_MEMBERS, password, reset=reset)

        self.stdout.write(self.style.SUCCESS("Demo data seeded."))

    def _guard_environment(self, *, force: bool) -> None:
        env = getattr(settings, "APP_ENV", "")
        if env not in ALLOWED_ENVIRONMENTS and not force:
            raise CommandError(
                f"Refusing to seed demo data: APP_ENV={env!r} is not a development environment. "
                "This command is for local development only. Re-run with --force only if you are "
                "absolutely certain this is not staging or production."
            )

    def _seed_tenant(
        self,
        tenant_spec: dict[str, str],
        members: Sequence[tuple[str, str, str]],
        password: str,
        *,
        reset: bool,
    ) -> None:
        tenant, _ = Tenant.objects.update_or_create(
            slug=tenant_spec["slug"],
            defaults={"name": tenant_spec["name"], "status": TenantStatus.ACTIVE},
        )
        self.stdout.write(f"tenant: {tenant.name} ({tenant.slug})")
        for email, name, role in members:
            user, created = self._upsert_user(email, name, password, reset=reset)
            Membership.objects.update_or_create(
                user=user,
                tenant=tenant,
                defaults={"role": role, "status": MembershipStatus.ACTIVE},
            )
            self.stdout.write(f"  member: {user.email} [{role}] ({self._state(created, reset)})")

    def _upsert_user(
        self,
        email: str,
        full_name: str,
        password: str,
        *,
        reset: bool,
        is_staff: bool = False,
    ) -> tuple[User, bool]:
        user, created = User.objects.get_or_create(
            email=email, defaults={"full_name": full_name, "is_staff": is_staff}
        )
        user.full_name = full_name
        user.is_staff = is_staff
        # Set the password only when creating the user, or when explicitly asked to reset.
        if created or reset:
            user.set_password(password)
        user.save()
        return user, created

    @staticmethod
    def _state(created: bool, reset: bool) -> str:
        if created:
            return "created"
        return "password reset" if reset else "updated, password kept"
