"""Database-layer isolation: PostgreSQL row-level security (master prompt §13-16, TEST 5-6).

These run with real transactions (transaction=True) so SET LOCAL / set_config behave exactly as
in production: context is established per transaction and reset when it ends. Rows are created as
the privileged login role (which bypasses RLS); reads happen under the unprivileged kayaka_app
role via tenant_context, where policies apply.
"""

import uuid

import pytest
from django.db import DatabaseError, connection

from kayaka.tenancy.db import current_tenant_id, tenant_context
from kayaka.tenancy.models import AuditLogEntry, Tenant, TenantScopedModel


def _seed() -> tuple[Tenant, Tenant]:
    tenant_a = Tenant.objects.create(name="Tenant A", slug="tenant-a-rls")
    tenant_b = Tenant.objects.create(name="Tenant B", slug="tenant-b-rls")
    AuditLogEntry.objects.create(tenant=tenant_a, action="a.event.1")
    AuditLogEntry.objects.create(tenant=tenant_a, action="a.event.2")
    AuditLogEntry.objects.create(tenant=tenant_b, action="b.event.1")
    return tenant_a, tenant_b


@pytest.mark.django_db(transaction=True)
def test_5_rls_blocks_cross_tenant_rows() -> None:
    tenant_a, tenant_b = _seed()

    with tenant_context(tenant_id=tenant_a.id):
        rows = list(AuditLogEntry.objects.all())
        assert len(rows) == 2
        assert all(row.tenant_id == tenant_a.id for row in rows)

    with tenant_context(tenant_id=tenant_b.id):
        rows = list(AuditLogEntry.objects.all())
        assert len(rows) == 1
        assert rows[0].tenant_id == tenant_b.id


@pytest.mark.django_db(transaction=True)
def test_5b_no_context_sees_no_tenant_rows() -> None:
    _seed()
    # Unprivileged role with no tenant GUC -> policy matches nothing.
    with tenant_context(tenant_id=None):
        assert AuditLogEntry.objects.count() == 0


@pytest.mark.django_db(transaction=True)
def test_5c_with_check_blocks_writing_into_another_tenant() -> None:
    tenant_a, tenant_b = _seed()
    # Attempt to write a row owned by tenant B while in tenant A's context -> RLS WITH CHECK fails.
    with pytest.raises(DatabaseError), tenant_context(tenant_id=tenant_a.id):
        AuditLogEntry.objects.create(tenant=tenant_b, action="smuggled")


@pytest.mark.django_db(transaction=True)
def test_6_tenant_context_does_not_leak_between_transactions() -> None:
    tenant_a, tenant_b = _seed()

    with tenant_context(tenant_id=tenant_a.id):
        assert current_tenant_id() == str(tenant_a.id)

    # After the transaction ends, the GUC is gone — nothing carried into the next transaction.
    assert current_tenant_id() == ""

    with tenant_context(tenant_id=tenant_b.id):
        assert current_tenant_id() == str(tenant_b.id)
        rows = list(AuditLogEntry.objects.all())
        assert {row.tenant_id for row in rows} == {tenant_b.id}

    assert current_tenant_id() == ""


@pytest.mark.django_db(transaction=True)
def test_6b_unknown_tenant_context_sees_nothing() -> None:
    _seed()
    with tenant_context(tenant_id=uuid.uuid7()):
        assert AuditLogEntry.objects.count() == 0


@pytest.mark.django_db(transaction=True)
def test_runtime_effective_role_is_unprivileged() -> None:
    """Inside tenant context the effective role is kayaka_app — not superuser, not BYPASSRLS —
    even though the login (session) role may be privileged in dev/CI. This is what makes RLS a
    real boundary rather than something a privileged connection silently skips."""
    with tenant_context(tenant_id=uuid.uuid7()), connection.cursor() as cursor:
        cursor.execute("SELECT current_user")
        assert cursor.fetchone()[0] == "kayaka_app"
        cursor.execute("SELECT rolsuper, rolbypassrls FROM pg_roles WHERE rolname = current_user")
        is_super, bypass_rls = cursor.fetchone()
        assert is_super is False
        assert bypass_rls is False


@pytest.mark.django_db
def test_every_tenant_scoped_table_is_rls_protected() -> None:
    """Meta-test enforcing RLS coverage: every concrete TenantScopedModel must have RLS enabled
    AND forced, at least one policy, and a tenant_id column. This fails CI the moment a future
    tenant-owned table is added without protection — the requirement is enforced, not assumed."""
    models = [m for m in TenantScopedModel.__subclasses__() if not m._meta.abstract]
    assert models, "expected at least one tenant-scoped model (AuditLogEntry)"

    with connection.cursor() as cursor:
        for model in models:
            table = model._meta.db_table
            cursor.execute(
                "SELECT relrowsecurity, relforcerowsecurity FROM pg_class WHERE relname = %s",
                [table],
            )
            row = cursor.fetchone()
            assert row is not None, f"table {table} not found"
            assert row[0] is True, f"{table}: RLS not ENABLED"
            assert row[1] is True, f"{table}: RLS not FORCED"

            cursor.execute("SELECT count(*) FROM pg_policies WHERE tablename = %s", [table])
            assert cursor.fetchone()[0] >= 1, f"{table}: no RLS policy"

            cursor.execute(
                "SELECT 1 FROM information_schema.columns "
                "WHERE table_name = %s AND column_name = 'tenant_id'",
                [table],
            )
            assert cursor.fetchone() is not None, f"{table}: missing tenant_id column"
