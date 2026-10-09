"""SQL builders for enabling row-level security on tenant-scoped tables.

Used from migrations. A protected table:
  * has RLS enabled AND forced (so even the table owner is subject to policies);
  * carries a ``tenant_id`` column;
  * is readable/writable only for rows whose ``tenant_id`` equals the ``kayaka.tenant_id`` GUC.

The policy compares against ``NULLIF(current_setting('app.tenant_id', true), '')::uuid``; when
the GUC is unset or empty the comparison is NULL, so no rows match — a request without tenant
context sees nothing in a protected table.
"""

from __future__ import annotations

TENANT_GUC = "app.tenant_id"


def enable_tenant_rls(table: str, *, policy: str | None = None) -> tuple[str, str]:
    """Return (forward_sql, reverse_sql) that enable/disable tenant RLS on ``table``."""
    policy_name = policy or f"{table}_tenant_isolation"
    guc = f"NULLIF(current_setting('{TENANT_GUC}', true), '')::uuid"
    forward = f"""
        ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;
        ALTER TABLE {table} FORCE ROW LEVEL SECURITY;
        DROP POLICY IF EXISTS {policy_name} ON {table};
        CREATE POLICY {policy_name} ON {table}
            USING (tenant_id = {guc})
            WITH CHECK (tenant_id = {guc});
    """
    reverse = f"""
        DROP POLICY IF EXISTS {policy_name} ON {table};
        ALTER TABLE {table} NO FORCE ROW LEVEL SECURITY;
        ALTER TABLE {table} DISABLE ROW LEVEL SECURITY;
    """
    return forward, reverse


def create_app_role_sql() -> tuple[str, str]:
    """Return (forward_sql, reverse_sql) creating the unprivileged ``kayaka_app`` runtime role.

    Idempotent: roles are cluster-global, so CREATE is guarded. The role is NOLOGIN — it is only
    ever entered via ``SET LOCAL ROLE`` from the privileged login role — and explicitly
    NOSUPERUSER / NOBYPASSRLS so RLS policies apply to it.
    """
    forward = """
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'kayaka_app') THEN
                CREATE ROLE kayaka_app
                    NOLOGIN NOSUPERUSER NOINHERIT NOCREATEDB NOCREATEROLE NOBYPASSRLS;
            END IF;
        END
        $$;
        GRANT USAGE ON SCHEMA public TO kayaka_app;
        GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO kayaka_app;
        GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO kayaka_app;
        ALTER DEFAULT PRIVILEGES IN SCHEMA public
            GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO kayaka_app;
        ALTER DEFAULT PRIVILEGES IN SCHEMA public
            GRANT USAGE, SELECT ON SEQUENCES TO kayaka_app;
    """
    # Keep the role on reverse (other databases/tests may rely on it); just revoke this schema's
    # privileges. Dropping a cluster-global role used elsewhere would be unsafe.
    reverse = """
        REVOKE ALL ON ALL TABLES IN SCHEMA public FROM kayaka_app;
        REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM kayaka_app;
        REVOKE USAGE ON SCHEMA public FROM kayaka_app;
    """
    return forward, reverse
