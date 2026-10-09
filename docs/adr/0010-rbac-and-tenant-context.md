# 0010. Permission-code RBAC and the Phase 2 tenant-context mechanism

- Status: Accepted
- Date: 2026-10-09
- Refines: [0002](0002-postgres-rls-multi-tenancy.md) (concrete mechanism; does not supersede the
  shared-schema + RLS decision)

## Context

Phase 2 implements identity, access and tenancy. ADR 0002 fixed the strategy (shared schema,
`tenant_id` everywhere, RLS, transaction-local context). This ADR records the concrete decisions
made while implementing it, so later phases build on one consistent model.

## Decision

### Authorization is expressed in permission codes

- A fixed vocabulary of permission codes lives in `kayaka.authorization.permissions`
  (e.g. `catalog.update`, `tenant.manage_members`, `platform.tenants.view`).
- Two disjoint role enums map to code sets in `kayaka.authorization.roles`:
  - **Tenant roles**: `OWNER`, `MANAGER`, `STAFF`, `MARKETING` → only `*.` tenant codes.
  - **Platform roles**: `PLATFORM_ADMIN`, `SUPPORT`, (`ANALYST` reserved, no codes yet) →
    only `platform.*` codes.
- Scopes never cross: a tenant role can never satisfy a platform code and vice versa. A test
  asserts this invariant.
- Views and the frontend ask about **codes**, never role names. `is_staff`/`is_superuser` are
  not Kayaka roles — they only gate Django admin.
- Platform roles are stored explicitly in `accounts.PlatformRoleAssignment` (user ↔ role), not
  on flags.

### Tenant context is explicit and membership-validated

- The authoritative tenant for a request is an **explicit tenant id**, resolved through
  `kayaka.tenancy.access.resolve_authorized_tenant(user, tenant_id)`, which returns the tenant
  only if the user has an **active membership** in it. A guessed/changed id, slug, header or
  query param that the user is not a member of resolves to nothing (404).
- For the dashboard, the user's chosen tenant is stored **server-side in the session**
  (`active_tenant_id`) and re-validated against membership on every read and on every switch. It
  is per-user session state, never a global/process-level "current tenant" (which is banned).
- This refines ADR 0002's illustrative `X-Tenant-ID` header: we prefer explicit path ids +
  session-stored active tenant, so there is no client-settable tenant header to reason about.

### RLS enforcement role (resolves the two-credential vs SET-ROLE discrepancy)

ADR 0002 called for **separate migration and runtime credentials**; the implementation adds a
`SET LOCAL ROLE`. These are complementary, not conflicting:

- **Production** uses the two credentials ADR 0002 intended — a migrator/owner role (migrate Job)
  and a dedicated unprivileged `kayaka_app` `LOGIN` role (runtime service). See
  deployment-staging.md.
- The app **also** runs `SET LOCAL ROLE kayaka_app` on every tenant request. When the runtime
  already connects as `kayaka_app` this is a harmless self-set; in local dev/CI (one superuser
  connection) it drops privileges so RLS still applies. The *effective* role is always
  `kayaka_app`.

So:

- Runtime queries run as the unprivileged **`kayaka_app`** role (NOSUPERUSER, NOBYPASSRLS), so
  RLS policies apply. DDL/migrations and the seed command run as the owner/superuser role, which
  bypasses RLS by design.
- The app enters the role transaction-locally with `SET LOCAL ROLE kayaka_app` and sets
  `app.tenant_id` / `app.user_id` with `set_config(..., true)` inside the request transaction
  (`kayaka.tenancy.db`). Everything resets when the transaction ends — safe under connection
  pooling, no leakage between requests. Session-level `SET` is banned.
- In dev/test the login role is the superuser, which can `SET ROLE` into `kayaka_app`; in
  staging/production the app's login role is a non-owner that is `GRANT`ed membership in
  `kayaka_app`.
- RLS policies are `FORCE`d and fail-closed:
  `tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid`. No context ⇒ no rows.

## Consequences

- One place to reason about "who can do what" (codes + maps), independent of UI.
- Defense in depth: even a missing application filter cannot cross tenants, because RLS runs as
  `kayaka_app`.
- The `kayaka_app` grant must exist in every environment; documented in prod settings.
- Phase 2 anchors RLS on `audit_log_entries` (the first tenant-scoped table). Future tenant
  tables inherit `TenantScopedModel` and call `enable_tenant_rls(...)` in their migration.

## Alternatives considered

- **Client-sent `X-Tenant-ID` header** (ADR 0002's illustration): works when validated, but adds
  a client-settable input to secure; session-stored active tenant avoids it.
- **Role-name checks in views** (`if role == "OWNER"`): rejected — brittle, scatters policy, and
  can't express partial grants. Permission codes centralize it.
- **A separate app login role instead of `SET LOCAL ROLE`**: also valid; we use `SET LOCAL ROLE`
  so one `DATABASE_URL` works for both migrations (owner) and runtime (dropped to `kayaka_app`).
