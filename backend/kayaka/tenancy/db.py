"""Transaction-local tenant context for PostgreSQL row-level security (ADR 0010).

The application connects as a privileged login role (dev/test: the superuser `kayaka`), but every
tenant-aware request drops to the unprivileged ``kayaka_app`` role and sets two transaction-local
GUCs that RLS policies read:

    SET LOCAL ROLE kayaka_app;                    -- subject to RLS (not superuser/bypassrls)
    SELECT set_config('app.tenant_id', $1, true); -- active tenant, '' when none
    SELECT set_config('app.user_id',   $2, true); -- authenticated user, '' when anonymous

``SET LOCAL`` and ``set_config(..., is_local=true)`` are reset automatically when the surrounding
transaction ends, so context can never leak between pooled connections or across requests. There
is no session-level tenant state and no module-level/global "current tenant".
"""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from contextlib import contextmanager

from django.db import connections, transaction

# The unprivileged runtime role. A literal (never interpolated from user input) because role
# names cannot be passed as bound parameters.
APP_ROLE = "kayaka_app"

# GUC namespace matches ADR 0002 (`app.tenant_id`).
TENANT_GUC = "app.tenant_id"
USER_GUC = "app.user_id"


def _as_text(value: uuid.UUID | str | None) -> str:
    return str(value) if value else ""


def apply_tenant_context(
    using: str = "default",
    *,
    tenant_id: uuid.UUID | str | None,
    user_id: uuid.UUID | str | None,
) -> None:
    """Drop to the app role and set the tenant/user GUCs on the current transaction.

    Must be called inside an open transaction (ATOMIC_REQUESTS provides one around every view).
    """
    connection = connections[using]
    with connection.cursor() as cursor:
        cursor.execute(f"SET LOCAL ROLE {APP_ROLE}")
        cursor.execute("SELECT set_config(%s, %s, true)", [TENANT_GUC, _as_text(tenant_id)])
        cursor.execute("SELECT set_config(%s, %s, true)", [USER_GUC, _as_text(user_id)])


@contextmanager
def tenant_context(
    *,
    tenant_id: uuid.UUID | str | None = None,
    user_id: uuid.UUID | str | None = None,
    using: str = "default",
) -> Iterator[None]:
    """Open a transaction, drop to the app role, set tenant/user GUCs, and run the block.

    Use in services, management commands and tests that need RLS enforcement outside the request
    cycle. On exit the transaction ends and ``SET LOCAL``/``set_config(local)`` reset.
    """
    with transaction.atomic(using=using):
        apply_tenant_context(using, tenant_id=tenant_id, user_id=user_id)
        yield


def current_tenant_id(using: str = "default") -> str:
    """Read the tenant GUC on the current connection ('' when unset). For tests/diagnostics."""
    connection = connections[using]
    with connection.cursor() as cursor:
        cursor.execute("SELECT current_setting(%s, true)", [TENANT_GUC])
        row = cursor.fetchone()
    return (row[0] or "") if row else ""
