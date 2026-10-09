"""Row-level security foundation.

Creates the unprivileged ``kayaka_app`` runtime role, grants it DML on the schema, and enables
forced RLS on ``audit_log_entries`` (the Phase 2 tenant-scoped table). The policy keys on the
transaction-local ``kayaka.tenant_id`` GUC set by ``kayaka.tenancy.db``. Later tenant-scoped
tables reuse ``kayaka.tenancy.rls.enable_tenant_rls`` in their own migrations.
"""

from django.db import migrations

from kayaka.tenancy.rls import create_app_role_sql, enable_tenant_rls

_role_forward, _role_reverse = create_app_role_sql()
_audit_forward, _audit_reverse = enable_tenant_rls("audit_log_entries")


class Migration(migrations.Migration):
    dependencies = [
        ("tenancy", "0001_initial"),
    ]

    operations = [
        migrations.RunSQL(sql=_role_forward, reverse_sql=_role_reverse),
        migrations.RunSQL(sql=_audit_forward, reverse_sql=_audit_reverse),
    ]
