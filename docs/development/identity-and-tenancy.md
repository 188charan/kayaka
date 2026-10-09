# Identity, access & tenancy (Phase 2)

How authentication, tenancy and authorization fit together. Decisions are recorded in
[ADR 0002](../adr/0002-postgres-rls-multi-tenancy.md),
[ADR 0003](../adr/0003-session-auth-same-origin-proxy.md),
[ADR 0010](../adr/0010-rbac-and-tenant-context.md) and
[ADR 0011](../adr/0011-allauth-headless-via-proxy.md).

## The shape

```
            User (global identity, accounts.User)
              │
     ┌────────┴─────────┐
Platform roles      Memberships (user ↔ tenant, with a tenant role)
(PlatformRole-        │
 Assignment)     ┌────┴────┐
     │         Tenant A   Tenant B
     ▼            │          │
platform.*     tenant role tenant role
permissions       │          │
                  ▼          ▼
             permission codes  →  tenant context  →  PostgreSQL RLS  →  isolated rows
```

- **Identity is global.** One `accounts.User` can belong to several tenants. `tenant_id` is
  never on `User`.
- **Membership** (`kayaka.tenancy.Membership`) links a user to a tenant with a `TenantRole`
  (`OWNER`/`MANAGER`/`STAFF`/`MARKETING`) and a status (`ACTIVE`/`INVITED`/`SUSPENDED`). One row
  per (user, tenant), enforced by a DB unique constraint.
- **Platform roles** (`PLATFORM_ADMIN`, `SUPPORT`; `ANALYST` reserved) are stored in
  `accounts.PlatformRoleAssignment`, separate from tenant membership and from `is_staff`.

## Authentication

Session-based, via **django-allauth headless** (ADR 0011). The browser only talks to the Next.js
origin; the proxy forwards `/api/v1/*` and `/_allauth/*` to Django.

Login flow (frontend `src/lib/auth/client.ts`):

1. `GET /api/v1/auth/csrf` → sets the readable `kayaka_csrftoken` cookie.
2. `POST /_allauth/browser/v1/auth/login` with `X-CSRFToken` and `{email, password}` → Django
   sets the `HttpOnly` session cookie.
3. `GET /api/v1/me` → identity, memberships, permissions, active tenant.

Logout: `DELETE /_allauth/browser/v1/auth/session`. The session cookie is `HttpOnly` and never
visible to JavaScript; only the CSRF cookie is readable (by design).

### CSRF

All unsafe methods (POST/PUT/PATCH/DELETE) require a valid `X-CSRFToken` matching the CSRF
cookie. DRF `SessionAuthentication` enforces this for authenticated requests; a test proves an
unsafe request without a token is rejected with `CSRF_FAILED`. CSRF is never disabled and
`@csrf_exempt` is never used.

## Authorization (permission-code RBAC)

Everything is checked against **permission codes**, never role names.

- Codes: `kayaka.authorization.permissions` (e.g. `catalog.update`, `tenant.manage_members`,
  `platform.tenants.view`).
- Role → code maps: `kayaka.authorization.roles` (`TENANT_ROLE_PERMISSIONS`,
  `PLATFORM_ROLE_PERMISSIONS`).
- The one check: `kayaka.tenancy.access.has_permission(user, code, tenant=...)`. Platform codes
  ignore `tenant`; tenant codes require an active membership in an active tenant.
- DRF permission classes: `kayaka.tenancy.permissions.platform_permission_required(code)` and
  `tenant_permission_required(code)`.
- **Frontend permission checks are UX only.** The backend is always authoritative.

Role → permissions summary:

| Role | Highlights |
|---|---|
| OWNER | full tenant: profile, members, settings, catalog CRUD, storefront, inquiries, customers, analytics |
| MANAGER | catalog CRUD, inquiries, customers, analytics, storefront view/edit (no members/settings) |
| STAFF | catalog view/update, inquiries, customers (no delete, no members, no settings) |
| MARKETING | storefront view/edit/publish, analytics (no catalog create) |
| PLATFORM_ADMIN | platform tenants view/manage, audit, health |
| SUPPORT | platform tenants view, health |

## Tenant context & RLS

See ADR 0010. The authoritative tenant is an explicit id resolved via
`resolve_authorized_tenant(user, tenant_id)` (returns the tenant only with an active membership).
The dashboard stores the chosen tenant in the **session** (`active_tenant_id`), re-validated on
every use and every switch — never a global/process "current tenant".

Row-level security:

- Runtime queries run as the unprivileged `kayaka_app` role; migrations/seed run as the owner.
- `kayaka.tenancy.db.tenant_context(tenant_id=…, user_id=…)` (and the request-time
  `apply_tenant_context`) issue `SET LOCAL ROLE kayaka_app` + `set_config('app.tenant_id', …,
  true)` inside the transaction. Everything resets at transaction end — leak-free under pooling.
- Policies are `FORCE`d and fail-closed; no context ⇒ no rows. Anchored on `audit_log_entries`;
  future tenant tables inherit `TenantScopedModel` and call `rls.enable_tenant_rls(...)`.

### Database identities & why the runtime cannot bypass RLS

Two credentials (ADR 0002/0010); see also
[deployment-staging.md](deployment-staging.md#database-roles-phase-2--rls):

1. **Migrations** run as the **owner/migrator** role (dev: superuser `kayaka`; prod: the Neon
   owner, used by the `kayaka-migrate-staging` Job).
2. **Application requests** run as **`kayaka_app`** (prod: a dedicated `LOGIN` role, used by the
   runtime service; dev/CI: the superuser connection dropped into `kayaka_app` via
   `SET LOCAL ROLE`).
3. **Tables and policies are owned** by the migrator/owner role.
4. **Bypass is prevented** because `kayaka_app` is `NOSUPERUSER` + `NOBYPASSRLS` and policies are
   `FORCE`d, so they apply even to a table owner. The *effective* role for every tenant query is
   `kayaka_app` — asserted by a test that reads `current_user`, `rolsuper` and `rolbypassrls`.
5. **Least privilege**: `kayaka_app` gets only `SELECT/INSERT/UPDATE/DELETE` on app tables (via
   migration `0002_rls` grants + `ALTER DEFAULT PRIVILEGES`), never ownership or DDL.
6. **CI** runs the RLS tests against real PostgreSQL and enters `kayaka_app` the same way prod
   does; `test_runtime_effective_role_is_unprivileged` fails if the effective role could bypass.
7. **Connection reuse / transactions**: context is set with `SET LOCAL` + `set_config(..., true)`
   (transaction-local), so it resets at COMMIT/ROLLBACK and never leaks across pooled connections
   — proven by `test_6_tenant_context_does_not_leak_between_transactions`.

### RLS coverage is enforced, not assumed

Phase 2 protects exactly one tenant-owned table — **`audit_log_entries`** — as the demonstration
and anchor. It is **not** proof that future tables are protected. Every new tenant-owned table
MUST:

1. inherit `TenantScopedModel` (gives it a `NOT NULL tenant_id`);
2. call `kayaka.tenancy.rls.enable_tenant_rls("<table>")` in its migration (enable + force RLS +
   policy);
3. rely on the `0002_rls` default grants (automatic for owner-created tables);
4. add an isolation test.

`test_every_tenant_scoped_table_is_rls_protected` scans all concrete `TenantScopedModel`
subclasses and fails CI if any lacks forced RLS, a policy, or a `tenant_id` column — so a future
unprotected table cannot ship silently.

> Management commands and any non-request code path that reads tenant-owned data must enter
> `tenant_context(...)` explicitly; otherwise they run as the owner (seed/migrations) and are not
> tenant-filtered. The request path handles this automatically in `BaseApiView`.

## Can Tenant A access Tenant B? No — four layers

1. **Authentication**: no session ⇒ 401; nothing tenant-scoped is reachable.
2. **Authorization**: `resolve_authorized_tenant` requires an active membership; a non-member
   gets 404 (existence not leaked). `has_permission` gates each action by code.
3. **Service/query layer**: selectors/views take the tenant explicitly from the authorized
   resolution, not from arbitrary request data.
4. **Database RLS**: even a missing filter cannot cross tenants — `kayaka_app` only sees rows
   whose `tenant_id` matches the transaction's `app.tenant_id`.

## API surface (Phase 2)

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | `/api/v1/auth/csrf` | public | set CSRF cookie |
| POST | `/_allauth/browser/v1/auth/login` | public | log in (allauth) |
| DELETE | `/_allauth/browser/v1/auth/session` | session | log out (allauth) |
| GET | `/api/v1/me` | session | identity, roles, permissions, memberships, active tenant |
| GET | `/api/v1/tenants` | session | tenants the user may see |
| GET | `/api/v1/tenants/{id}` | session | tenant detail (404 if not a member/platform viewer) |
| PATCH | `/api/v1/tenants/{id}` | session + `tenant.update` | rename a tenant |
| POST | `/api/v1/tenants/switch` | session | set active tenant (membership-validated) |
| GET | `/api/v1/platform/overview` | session + `platform.health.view` | platform-only overview |

## Local demo data & login

Seed the canonical personas (idempotent; password supplied, never stored):

```bash
# with the stack running (docker compose up --build --wait)
KAYAKA_DEMO_PASSWORD='change-me-locally' \
  docker compose run --rm -T backend python manage.py seed_demo_data
```

Then open the frontend (`cd frontend && npm run dev`) and sign in at `/login` as any persona
from [demo-accounts.md](demo-accounts.md) (e.g. `owner@demo.kayaka.local`). A user with
memberships in more than one tenant sees a tenant switcher in the dashboard header.

Seed safety: the command requires a password (no default in source, never logged), is idempotent,
and **refuses to run unless `APP_ENV` is a development/test environment** (override with `--force`).
Re-running does **not** reset existing users' passwords unless you pass `--reset-passwords`.

## Running the security tests

```bash
docker compose run --rm -T backend pytest kayaka/tenancy -q
```

Covers RBAC maps, the identity/tenancy APIs, the numbered cross-tenant isolation suite, RLS row
visibility, transaction-local context (no leakage), and CSRF enforcement.
