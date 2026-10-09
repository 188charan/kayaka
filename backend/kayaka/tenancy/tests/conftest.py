"""Shared fixtures for tenancy/identity/RBAC/RLS tests."""

from collections.abc import Callable

import pytest
from rest_framework.test import APIClient

from kayaka.accounts.models import PlatformRoleAssignment, User
from kayaka.authorization.roles import PlatformRole, TenantRole
from kayaka.tenancy.models import Membership, MembershipStatus, Tenant, TenantStatus

# Test-only password (never a real credential; ruff S105/S106 relaxed under tests/).
PASSWORD = "test-pass-ABCDEF-123456"

MakeUser = Callable[..., User]
MakeTenant = Callable[..., Tenant]
AddMember = Callable[..., Membership]


@pytest.fixture
def make_user(db: object) -> MakeUser:
    def _make(
        email: str,
        full_name: str = "",
        platform_role: str | None = None,
        is_staff: bool = False,
    ) -> User:
        user = User.objects.create_user(email, PASSWORD, full_name=full_name, is_staff=is_staff)
        if platform_role:
            PlatformRoleAssignment.objects.create(user=user, role=platform_role)
        return user

    return _make


@pytest.fixture
def make_tenant(db: object) -> MakeTenant:
    def _make(name: str, slug: str, status: str = TenantStatus.ACTIVE) -> Tenant:
        return Tenant.objects.create(name=name, slug=slug, status=status)

    return _make


@pytest.fixture
def add_member(db: object) -> AddMember:
    def _make(
        user: User, tenant: Tenant, role: str, status: str = MembershipStatus.ACTIVE
    ) -> Membership:
        return Membership.objects.create(user=user, tenant=tenant, role=role, status=status)

    return _make


@pytest.fixture
def tenant_a(make_tenant: MakeTenant) -> Tenant:
    return make_tenant("Anjali Jewellery & Décor", "anjali-jewellery")


@pytest.fixture
def tenant_b(make_tenant: MakeTenant) -> Tenant:
    return make_tenant("Namma Crafts", "namma-crafts")


@pytest.fixture
def tenant_c(make_tenant: MakeTenant) -> Tenant:
    return make_tenant("Third Co", "third-co")


@pytest.fixture
def owner_a(make_user: MakeUser, add_member: AddMember, tenant_a: Tenant) -> User:
    user = make_user("owner@demo.kayaka.local", "Anjali")
    add_member(user, tenant_a, TenantRole.OWNER)
    return user


@pytest.fixture
def manager_a(make_user: MakeUser, add_member: AddMember, tenant_a: Tenant) -> User:
    user = make_user("manager@demo.kayaka.local", "Rahul")
    add_member(user, tenant_a, TenantRole.MANAGER)
    return user


@pytest.fixture
def staff_a(make_user: MakeUser, add_member: AddMember, tenant_a: Tenant) -> User:
    user = make_user("staff@demo.kayaka.local", "Sneha")
    add_member(user, tenant_a, TenantRole.STAFF)
    return user


@pytest.fixture
def owner_b(make_user: MakeUser, add_member: AddMember, tenant_b: Tenant) -> User:
    user = make_user("owner@namma.kayaka.local", "Namma Owner")
    add_member(user, tenant_b, TenantRole.OWNER)
    return user


@pytest.fixture
def multi_user(
    make_user: MakeUser, add_member: AddMember, tenant_a: Tenant, tenant_b: Tenant
) -> User:
    """A user with active memberships in both tenant A and tenant B (never in tenant C)."""
    user = make_user("multi@demo.kayaka.local", "Multi")
    add_member(user, tenant_a, TenantRole.MANAGER)
    add_member(user, tenant_b, TenantRole.STAFF)
    return user


@pytest.fixture
def platform_admin(make_user: MakeUser) -> User:
    return make_user("admin@kayaka.local", "Charan", platform_role=PlatformRole.PLATFORM_ADMIN)


def login_as(user: User) -> APIClient:
    """Return an APIClient authenticated as `user` with a valid CSRF token primed."""
    client = APIClient()
    client.force_login(user, backend="django.contrib.auth.backends.ModelBackend")
    client.get("/api/v1/auth/csrf")
    token = client.cookies["kayaka_csrftoken"].value
    client.credentials(HTTP_X_CSRFTOKEN=token)
    return client
