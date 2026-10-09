# Staging deployment (prepared, not yet provisioned)

Nothing in this document has been provisioned yet. It depends on two open decisions from
blueprint §Y: a GCP billing account (card) for Cloud Run, and a domain. The workflow
[`deploy-staging.yml`](../../.github/workflows/deploy-staging.yml) is written and lints clean,
but has never run.

## Target topology (blueprint §T)

| Piece | Service | Notes |
|---|---|---|
| Frontend | Vercel (Hobby), Git integration | Root directory `frontend`; region `sin1` |
| Backend | Cloud Run `kayaka-api-staging`, `asia-southeast1` | min 0 / max 2 instances, 512 MiB |
| Migrations | Cloud Run Job `kayaka-migrate-staging` | Runs before each deploy |
| Database | Neon project `kayaka-staging` (Singapore) | Use the **pooled** connection string |
| Secrets | GCP Secret Manager | Referenced by name; never in GitHub |
| Images | Artifact Registry repo `kayaka` | Add a cleanup policy (keep the last 5) |

## One-time setup checklist

1. **GCP project** with billing, plus budget alerts at $1 and $5.
2. Enable APIs: Cloud Run, Artifact Registry, Secret Manager, IAM Credentials.
3. Artifact Registry Docker repo `kayaka` in `asia-southeast1`.
4. Service accounts:
   - `kayaka-deployer` (used by GitHub): Cloud Run Admin, Artifact Registry Writer, and
     Service Account User on the runtime account.
   - `kayaka-runtime` (used by Cloud Run): Secret Manager Secret Accessor.
5. **Workload Identity Federation** pool + provider for GitHub OIDC, restricted to this repo,
   and allowed to impersonate `kayaka-deployer`. No JSON keys.
6. **Neon** project `kayaka-staging`, region Singapore. Copy the pooled connection string, then append
   `?sslmode=require`.
7. **Secret Manager** secrets:
   - `kayaka-staging-database-url`
   - `kayaka-staging-django-secret-key`: `python -c "import secrets; print(secrets.token_urlsafe(50))"`
   - `kayaka-staging-proxy-secret`: `openssl rand -hex 32` (also set in Vercel, see below)
8. **GitHub environment `staging`** with these *variables* (not secrets; none are sensitive):

   | Variable | Example |
   |---|---|
   | `GCP_PROJECT_ID` | `kayaka-staging-123456` |
   | `GCP_REGION` | `asia-southeast1` |
   | `GCP_WIF_PROVIDER` | `projects/123/locations/global/workloadIdentityPools/github/providers/kayaka` |
   | `GCP_DEPLOY_SERVICE_ACCOUNT` | `kayaka-deployer@<project>.iam.gserviceaccount.com` |
   | `GCP_RUNTIME_SERVICE_ACCOUNT` | `kayaka-runtime@<project>.iam.gserviceaccount.com` |
   | `API_HOST` | `kayaka-api-staging-xxxx.a.run.app` (the Cloud Run host; see note) |
   | `FRONTEND_ORIGIN` | `https://kayaka-staging.vercel.app` |

9. **Vercel** project: root directory `frontend`, function region `sin1`, environment variables
   for *Preview*: `API_ORIGIN=https://<API_HOST>`, `PROXY_SHARED_SECRET=<same as Secret Manager>`,
   `APP_ENV=staging`.

10. Run **Actions → Deploy backend (staging) → Run workflow**. It builds the `prod` image, runs
    migrations, deploys, and smoke-tests `/readyz` and `/api/v1/public/ping`.

### Note on `DJANGO_ALLOWED_HOSTS`

The Next.js proxy forwards requests with `Host` set to the **API** host (verified locally; the
original host is in `X-Forwarded-Host`). So `DJANGO_ALLOWED_HOSTS` only needs the Cloud Run host,
and later the API custom domain. `USE_X_FORWARDED_HOST` stays off.

## Database roles (Phase 2 — RLS)

RLS is only a real boundary if the **runtime** database identity cannot bypass it. The design
uses two credentials (ADR 0002, ADR 0010):

| Identity | Used by | Privileges |
|---|---|---|
| **migrator** (owner) | the `kayaka-migrate-staging` Cloud Run **Job** | owns schema/tables/policies; runs DDL. On Neon this is the project's owner role. |
| **`kayaka_app`** (runtime) | the `kayaka-api-staging` Cloud Run **service** | `LOGIN`, `NOSUPERUSER`, `NOBYPASSRLS`; only DML on tenant/app tables; owns nothing. Subject to every RLS policy. |

Provision once (as the Neon owner), **before** the first migrate job:

```sql
-- Unprivileged runtime role. If it already exists, migration 0002_rls just (re)applies grants.
CREATE ROLE kayaka_app LOGIN PASSWORD '<generate: openssl rand -base64 24>'
    NOSUPERUSER NOINHERIT NOCREATEDB NOCREATEROLE NOBYPASSRLS;
GRANT CONNECT ON DATABASE <db> TO kayaka_app;
-- Table/sequence grants + ALTER DEFAULT PRIVILEGES are applied by migration 0002_rls,
-- running as the migrator (owner) role.
```

Two `DATABASE_URL` secrets:

- `kayaka-staging-database-url-migrate` → migrator role → used by the migrate **Job**.
- `kayaka-staging-database-url` → `kayaka_app` role → used by the runtime **service**.

The application always runs `SET LOCAL ROLE kayaka_app` at the start of a tenant request
(`kayaka.tenancy.db`). When the runtime already connects as `kayaka_app` this is a harmless
self-set; in local dev (single superuser connection) it drops privileges so RLS still applies.
Either way the **effective** role for tenant queries is `kayaka_app`, which cannot bypass RLS.

> Local dev and CI use a single superuser Postgres role for convenience, but every tenant query
> still runs *as* `kayaka_app` via `SET LOCAL ROLE`, and the test suite asserts that the effective
> role is not a superuser and does not have `BYPASSRLS`
> (`kayaka/tenancy/tests/test_rls.py::test_runtime_effective_role_is_unprivileged`).

## Not in Phase 1

- Production environment (same steps with `production` names, plus a required reviewer on the
  GitHub environment).
- Scheduled jobs (rollups, cleanup, backups): Phase 8 / Phase 9.
- Custom domains, R2, Resend, Sentry: when their phases need them.
