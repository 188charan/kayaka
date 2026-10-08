# 0002. Shared-schema multi-tenancy with PostgreSQL RLS

- Status: Accepted
- Date: 2026-09-30

## Context

Every entrepreneur is a tenant. Tenant A must never read or change tenant B's data. A single
leak would destroy trust in the platform. The free-tier database is small (0.5 GB on Neon),
which rules out a database or schema per tenant.

## Decision

- **PostgreSQL** is the single source of truth.
- **Shared database, shared schema.** Every tenant-owned table has `tenant_id uuid NOT NULL`,
  and `tenant_id` leads its main indexes.
- Isolation is enforced at several layers:
  1. Tenant context is resolved server-side (public: store slug; dashboard: `X-Tenant-ID`
     validated against the user's membership; platform: staff role). `tenant_id` is never
     read from request bodies.
  2. Every view declares required permission codes.
  3. Selectors and services take the tenant explicitly.
  4. Related IDs in payloads are resolved through tenant-scoped lookups.
  5. **Composite foreign keys** `(tenant_id, parent_id) → parent(tenant_id, id)` for
     same-tenant relations.
  6. **Row-Level Security** on every tenant-owned table, forced and fail-closed:
     `tenant_id = current_setting('app.tenant_id', true)::uuid` (or explicit platform access).
     The runtime DB role is not the table owner and has no `BYPASSRLS`. Migrations run as the
     owner role.
  7. Context is set with transaction-local `set_config(..., true)` inside the request
     transaction, which is safe with PgBouncer transaction pooling. Session-level `SET` is banned.
- A blocking **isolation test suite** (endpoint matrix, RLS tests, and meta-tests that fail if a
  tenant table lacks RLS or a view lacks permissions) runs in CI.

Phase 1 creates no tenant tables. The DB role split and RLS helpers arrive at the start of
Phase 2, before any tenant-owned table exists.

## Consequences

- Strong defense in depth. An application bug alone doesn't leak data.
- More moving parts: two DB roles, RLS policies in migrations, and tenant context in jobs and tests.
- A small per-query overhead from RLS predicates.
- Cross-tenant work (platform analytics, rollups) must explicitly enter platform context,
  which is audited.

## Alternatives considered

- **Schema per tenant / DB per tenant:** stronger isolation, but doesn't fit free-tier
  limits, makes migrations N times slower, and complicates platform analytics.
- **Application filtering only:** simpler, but a single missing filter leaks data.
