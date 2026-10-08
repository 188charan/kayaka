# Kayaka — Complete Project Overview

A full, inch-by-inch technical reference for the `kayaka` repository as it stands today. Every claim below is grounded in files that were read directly; exact paths and symbol names are used throughout. Where something is a placeholder, stub, or deferred to a later phase, it is called out explicitly.

---

## 1. Summary (read this first)

**What it is.** Kayaka is a multi-tenant commerce platform for small entrepreneurs. Each business gets its own persistent, searchable, customizable storefront, and customers send inquiries over WhatsApp instead of paying online. This is stated in `README.md` and expanded in `docs/architecture/blueprint.md`.

**What exists today.** The repository is at **Phase 1 — "foundation / walking skeleton"** (per `README.md` and `docs/architecture/overview.md`). That means the full-stack plumbing is built and proven end-to-end, but **no business features exist yet**. Concretely:

- **Backend** (`backend/`): Django 5.2 + Django REST Framework modular monolith. Two app modules exist — `kayaka.core` (error envelope, request IDs, proxy trust, health probes, logging, one public `ping` endpoint) and `kayaka.accounts` (a custom `User` model). The only business-facing API endpoint is `GET /api/v1/public/ping`. No tenant, product, order, or auth endpoints exist yet.
- **Frontend** (`frontend/`): Next.js 16 (App Router) + React 19 + TypeScript + Tailwind v4 + shadcn/ui. Four route groups exist as shells: marketing landing, storefront, tenant dashboard, platform admin. All of them render placeholders; their only live behaviour is an "API connected" status check.
- **Integration**: A same-origin proxy (`frontend/src/proxy.ts`) forwards `/api/v1/*` to Django with a shared secret. A typed client is generated from the backend's OpenAPI schema.
- **Infra & quality**: Docker Compose dev stack (Postgres 17 + Mailpit + Django), a thorough CI pipeline (lint, types, module boundaries, tests, schema drift, secret scanning), and a prepared-but-never-run Cloud Run staging deploy.

**Overall maturity.** The engineering scaffolding is unusually mature and disciplined for a Phase 1 project: strict typing, enforced module boundaries, pinned dependencies, a committed API contract, defense-in-depth security defaults, and ~52 backend + ~30 frontend unit tests + 9 E2E scenarios. The *product* surface, by contrast, is intentionally empty.

**The single most important caveat.** The multi-tenancy, RBAC, and PostgreSQL Row-Level-Security isolation that the architecture is built around are **designed but not implemented** — they start in Phase 2. Today there is exactly one user table and no tenant tables.

---

## 2. Repository layout

From the filesystem (ignoring `.git`, `node_modules`, `.next`, and Python caches):

```
kayaka/
├── README.md                 project intro + quick start
├── Makefile                  convenience targets (wrap docker compose / npm)
├── compose.yaml              local dev stack: db + mailpit + backend
├── .editorconfig             2-space default, 4 for Python, tabs for Makefile
├── .env.example              root compose overrides (proxy secret, ports, log format)
├── .gitignore
├── .github/
│   ├── dependabot.yml        weekly grouped updates (uv, npm, docker, compose, actions)
│   └── workflows/
│       ├── ci.yml            backend / frontend / e2e / secrets jobs
│       └── deploy-staging.yml manual Cloud Run deploy (prepared, not yet run)
├── backend/                  Django 5.2 + DRF modular monolith
├── frontend/                 Next.js 16 app (4 route groups)
└── docs/                     blueprint, ADRs, development guides
```

Git history is short: `17b9fa1` (merge), `ed5d609` (initial commit), `8431efd` (file upload) on branch `main`, with an `origin` at `github.com/188charan/kayaka`.

---

## 3. Top-level configuration & tooling

### 3.1 README and quick start

`README.md` describes the product in one line, states Phase 1 is complete with "No business features yet," and gives the two-command local setup: `docker compose up --build --wait` (Postgres + Mailpit + Django on `:8000`), then `npm run dev` in `frontend/` (Next.js on `:3000`). Opening `http://localhost:3000` should display **"API connected"**.

### 3.2 Makefile

Thin wrappers over the real commands. `BACKEND = docker compose run --rm -T backend`.

| Target | What it does |
|---|---|
| `up` / `down` / `logs` | start (detached, `--wait`), stop (keeps `pgdata`), follow backend logs |
| `backend-shell` | bash inside the backend container |
| `backend-check` | `ruff check` + `ruff format --check` + `lint-imports` + `mypy` + `makemigrations --check` (test settings) |
| `backend-test` | `pytest` |
| `schema` | regenerate `backend/openapi/schema.json` via `spectacular`, then `npm run api:generate` |
| `frontend-check` | `lint` + `format:check` + `typecheck` + `test` + `build` |
| `e2e` | `npm run test:e2e` (needs `make up` and a built frontend) |
| `check` | everything above in sequence |

### 3.3 Environment configuration

- Root `.env.example`: `PROXY_SHARED_SECRET` (must match the frontend), host ports (`POSTGRES_PORT`, `BACKEND_PORT`, `MAILPIT_UI_PORT`, `MAILPIT_SMTP_PORT`), and `LOG_FORMAT` (`console` or `json`). Every value has a working default; the file warns against real secrets.
- `frontend/.env.example` and `frontend/.env.local` (identical content currently): `API_ORIGIN=http://localhost:8000`, `PROXY_SHARED_SECRET=dev-only-proxy-secret-0123456789abcdef`, `APP_ENV=development`. Validated at startup by `src/lib/env-schema.ts`.
- `.editorconfig`: UTF-8, LF, final newline, trim trailing whitespace; 2-space indent default, 4 for `*.py`, tab for `Makefile`.
- `.gitignore`: ignores `.env*` (except `.env.example`), keys/pems, Python caches, `backend/staticfiles/`, `node_modules/`, `frontend/.next/`, `frontend/out/`, coverage/test-results/reports, `*.tsbuildinfo`.

> **Observation:** `frontend/.env.local` is present in the working tree and is git-ignored, so it won't be committed. It carries only a dev placeholder secret, so there's no leak, but note that a real `.env.local` exists on this machine.

### 3.4 Docker Compose dev stack (`compose.yaml`)

Project name `kayaka`. All ports bind to `127.0.0.1` only.

| Service | Image | Purpose / notes |
|---|---|---|
| `db` | `postgres:17.11-alpine` | DB `kayaka` / user `kayaka` / pw `kayaka`; `pgdata` volume; `pg_isready` healthcheck |
| `mailpit` | `axllent/mailpit:v1.31.3` | Dev SMTP + web UI (`:8025` / `:1025`) |
| `backend` | built from `backend/Dockerfile` target `dev` | runs `migrate` then `runserver 0.0.0.0:8000`; source bind-mounted (`./backend:/app`); `DJANGO_SETTINGS_MODULE=config.settings.dev`; `DATABASE_URL`, `EMAIL_URL=smtp://mailpit:1025`, `DJANGO_ADMIN_ENABLED=true`; healthcheck hits `/readyz` |

`backend` depends on `db` being healthy and `mailpit` started.

---

## 4. CI/CD pipeline

### 4.1 CI — `.github/workflows/ci.yml`

Triggers on pushes to `main` and all pull requests. `permissions: contents: read`; concurrency cancels superseded runs. CI-only placeholder env vars (`PROXY_SHARED_SECRET`, `API_ORIGIN`, `APP_ENV=test`). All actions are pinned to commit SHAs.

| Job | Runner | Key steps |
|---|---|---|
| **backend** | ubuntu-24.04, Postgres 17.11 service | `astral-sh/setup-uv` (uv 0.12.21, Python 3.14.7) → `uv sync --locked` → ruff lint (GitHub format) → ruff format check → **import-linter** (`lint-imports`) → **mypy** → `makemigrations --check` (test settings) → **`check --deploy --fail-level WARNING`** with prod settings and dummy prod env → `pytest` → regenerate `openapi/schema.json` and fail if it drifts |
| **frontend** | ubuntu-24.04 | `setup-node` from `frontend/.nvmrc` → `npm ci` → ESLint → Prettier `--check` → `typecheck` → regenerate `src/lib/api/schema.d.ts` and fail if it drifts → Vitest → `next build` |
| **e2e** | ubuntu-24.04, `needs: [backend, frontend]` | `docker compose up --build --wait` → `npm ci` → `playwright install chromium` → `next build` → Playwright (desktop + mobile); uploads `playwright-report` on failure |
| **secrets** | ubuntu-24.04 | `gitleaks:v8.30.1` over full git history (`--redact`) |

Per `docs/development/ci.md`: the workflow passes `actionlint` and every job's steps have been run locally in clean containers, **but the workflow has never actually run on GitHub** (there was no remote at the time of writing). `uv.lock` and `package-lock.json` are committed; Dependabot proposes weekly grouped updates.

### 4.2 Staging deploy — `.github/workflows/deploy-staging.yml`

`workflow_dispatch` only (manual). **Status: written, lints clean, never run.** It needs one-time GCP setup documented in `docs/development/deployment-staging.md`.

Target topology: backend as a container on **Google Cloud Run** (`kayaka-api-staging`, region `asia-southeast1`, min 0 / max 2, 512 MiB), migrations via a Cloud Run **Job** (`kayaka-migrate-staging`), **Neon** Postgres (Singapore), secrets in **GCP Secret Manager**, images in Artifact Registry. Auth to GCP uses **Workload Identity Federation** (OIDC, `id-token: write`), so no long-lived JSON keys. The frontend deploys separately through **Vercel's** Git integration, not this workflow. Final steps smoke-test `/readyz` and `/api/v1/public/ping`.

---

## 5. Backend (`backend/`)

### 5.1 Stack, Python version, and dependencies (`pyproject.toml`)

- Package name `kayaka-backend` v0.1.0; `requires-python = ">=3.14,<3.15"`.
- Managed with **uv** (`[tool.uv] package = false`), lockfile `uv.lock` committed.

**Runtime dependencies (all pinned with `==`):**

| Package | Version | Role |
|---|---|---|
| `django` | 5.2.17 | Web framework (LTS) |
| `djangorestframework` | 3.16.1 | REST API layer |
| `drf-spectacular` | 0.30.0 | OpenAPI 3 schema → typed frontend client |
| `django-environ` | 0.14.0 | Env-based settings; parses `DATABASE_URL` / `EMAIL_URL` |
| `psycopg[binary]` | 3.3.6 | PostgreSQL driver |
| `python-json-logger` | 4.2.0 | Structured JSON logs |
| `argon2-cffi` | 25.1.0 | Argon2 password hashing |
| `gunicorn` | 26.2.0 | Production WSGI server |

**Dev dependencies:** `pytest` 9.1.1, `pytest-django` 4.14.0, `ruff` 0.16.9, `mypy` 1.19.1, `django-stubs` 5.2.9, `djangorestframework-stubs` 3.16.9, `import-linter` 2.15.

**Tooling config in `pyproject.toml`:**

- **ruff**: `target-version = py314`, line length 100, migrations excluded. Lint rule families: `E/W/F`, `I` (isort), `B` (bugbear), `UP` (pyupgrade), `DJ` (django), `S` (bandit security), `SIM`, `DTZ` (tz-aware datetimes), `T20` (no `print`), `PT` (pytest style), `RUF`. Tests relax `S101/S105/S106`; settings relax `S105`.
- **mypy**: `strict = true`, `python_version 3.14`, Django + DRF plugins, `warn_unreachable`. `disallow_subclassing_any = false` (Django base classes are only partly typed). Tests and `conftest` relax untyped-def rules. `django-stubs` points at `config.settings.test`.
- **pytest**: `--ds=config.settings.test` is forced (so it wins over the compose `DJANGO_SETTINGS_MODULE`), `testpaths = ["kayaka"]`, `filterwarnings = ["error"]` (warnings are hard failures).
- **import-linter** (`[tool.importlinter]`): root packages `kayaka`, `config`. Two contracts:
  1. *Layers*: `kayaka.accounts` sits above `kayaka.core` (core is the lowest layer).
  2. *Forbidden*: `kayaka` modules may not import `config` (settings come via `django.conf.settings`).

### 5.2 Dockerfile (`backend/Dockerfile`)

Multi-stage, `# syntax=docker/dockerfile:1.7`, base image `python:3.14.7-slim-trixie`, uv copied from `ghcr.io/astral-sh/uv:0.12.21`.

- **base**: env for uv (`UV_PROJECT_ENVIRONMENT=/opt/venv`, bytecode compile, no Python downloads).
- **dev**: `uv sync --locked` (all deps), copies source, `DJANGO_SETTINGS_MODULE=config.settings.dev`, runs `runserver`.
- **prod-deps**: `uv sync --locked --no-dev` (runtime deps only).
- **prod**: fresh base image, non-root user `app` (uid/gid 10001), copies the venv, `DJANGO_SETTINGS_MODULE=config.settings.prod`, launches **gunicorn** (`config.wsgi:application`, configurable workers/threads/timeout, binds `$PORT` for Cloud Run).

`.dockerignore` excludes venvs, caches, `staticfiles`, `.env*`, and the Dockerfile itself.

### 5.3 Settings (`backend/config/settings/`)

Split by environment; `__init__.py` is empty. `manage.py` defaults to `config.settings.dev`; `wsgi.py`/`asgi.py` default to `config.settings.prod`.

**`base.py` — shared.** Highlights:

- `env = environ.Env()`; all runtime config comes from env vars.
- `INSTALLED_APPS`: `django.contrib.auth`, `contenttypes`, `sessions`, `messages`, `staticfiles`, `rest_framework`, `drf_spectacular`, `kayaka.accounts`. `django.contrib.admin` is prepended **only** when `DJANGO_ADMIN_ENABLED=true`.
- `MIDDLEWARE` (order matters): `RequestContextMiddleware` → `TrustedProxyMiddleware` → Django `SecurityMiddleware` → `ContentSecurityPolicyMiddleware` → `SessionMiddleware` → `CommonMiddleware` → `CsrfViewMiddleware` → `AuthenticationMiddleware` → `MessageMiddleware` → `XFrameOptionsMiddleware`.
- `APPEND_SLASH = False` — URLs never end in a slash (e.g. `/api/v1/public/ping`).
- **Database**: parsed from `DATABASE_URL` (default local Postgres). `CONN_MAX_AGE=60`, `CONN_HEALTH_CHECKS=True`, and **`ATOMIC_REQUESTS=True`** (every request in a transaction — Phase 2 relies on this for transaction-local RLS tenant context, per ADR 0002).
- **Auth**: `AUTH_USER_MODEL = "accounts.User"`. Hashers lead with Argon2. Password validators include a 10-char minimum.
- **Sessions & CSRF** (ADR 0003): cookie `kayaka_session` (`HttpOnly`, `SameSite=Lax`, 14-day age); CSRF cookie `kayaka_csrftoken`; `CSRF_FAILURE_VIEW` returns the JSON envelope. `PROXY_SHARED_SECRET` default empty (empty disables proxy trust).
- **Security headers**: `X_FRAME_OPTIONS=DENY`, nosniff, referrer policy, COOP same-origin. `API_CONTENT_SECURITY_POLICY = "default-src 'none'; frame-ancestors 'none'"` (JSON-only API).
- **Email**: parsed from `EMAIL_URL` (default `consolemail://`), 10s timeout.
- **DRF** (`REST_FRAMEWORK`): session auth only; **default permission `IsAuthenticated` (default-deny)**; JSON renderer/parser only; `drf_spectacular` AutoSchema; custom `EXCEPTION_HANDLER` = `kayaka.core.api.errors.exception_handler`; **`NUM_PROXIES = 0`** (never trust `X-Forwarded-For`); test default format JSON.
- **drf-spectacular** (`SPECTACULAR_SETTINGS`): title "Kayaka API", `VERSION = "1.0.0"` (contract version, kept deterministic), schema served without the schema endpoint, `COMPONENT_SPLIT_REQUEST`, path prefix `/api/v1`.
- **Logging**: `build_logging_config` with level/format from env (`json` default).

**`dev.py`**: `DEBUG=True` default, insecure default secret key, `ALLOWED_HOSTS` includes `backend`, CSRF trusts `http://localhost:3000`, console log format, adds the **Browsable API** renderer, and sets `API_CONTENT_SECURITY_POLICY = None` (so the browsable API and admin can use inline styles).

**`test.py`**: `DEBUG=False`, fixed test secret, `APP_ENV="test"`, fast **MD5** password hasher, in-memory email backend, JSON logging at WARNING.

**`prod.py`**: `DEBUG=False`; `SECRET_KEY`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `PROXY_SHARED_SECRET` all **required** (fail-fast); enforces `PROXY_SHARED_SECRET` ≥ 32 chars; TLS terminates at Cloud Run via `SECURE_PROXY_SSL_HEADER`; `SECURE_SSL_REDIRECT=False` (deliberate — internal probes use HTTP); HSTS 1 year; secure session/CSRF cookies; silences two security system checks (`W008`, `W021`) with documented reasons.

### 5.4 URLs & API routing

**`config/urls.py`** (root):

| Path | View | Notes |
|---|---|---|
| `/healthz` | `kayaka.core.health.healthz` | Liveness, no DB |
| `/readyz` | `kayaka.core.health.readyz` | Readiness, checks DB |
| `/api/v1/` | `include("config.api_v1")` | API router |
| `settings.ADMIN_URL` | `admin.site.urls` | Only if `ADMIN_ENABLED` (default `django-admin/`) |

Django error handlers (`handler400/403/404/500`) are wired to the JSON-envelope functions in `kayaka.core.api.errors`, so even non-DRF failures return the standard error shape.

**`config/api_v1.py`** (`app_name = "api_v1"`):

- `public/ping` → `ping_view` (name `public-ping`).
- When `DEBUG`: adds `schema` (`SpectacularAPIView`) and `docs` (`SpectacularSwaggerView`).
- A trailing `re_path(r"^.*$", api_not_found)` catch-all returns the JSON `NOT_FOUND` envelope for any unknown `/api/v1/` URL — in **every** environment (unlike `handler404`, which is bypassed under `DEBUG`).

**Complete current API surface:**

| Method | Path | Auth | Handler | Response |
|---|---|---|---|---|
| GET | `/api/v1/public/ping` | None (`AllowAny`) | `PingView` | `{ "data": { service, version, environment, time } }`, `Cache-Control: no-store` |
| GET | `/api/v1/schema` | dev only | `SpectacularAPIView` | OpenAPI document |
| GET | `/api/v1/docs` | dev only | `SpectacularSwaggerView` | Swagger UI |
| * | `/api/v1/<anything-else>` | — | `api_not_found` | `404 NOT_FOUND` envelope |
| GET | `/healthz` | None | `healthz` | `{ "status": "ok" }` |
| GET | `/readyz` | None | `readyz` | `{ "status": "ok", "checks": {"database": "ok"} }` or `503` |
| * | `/django-admin/` | staff | Django admin | Only when `DJANGO_ADMIN_ENABLED=true` |

### 5.5 The `kayaka.core` module

Lowest layer; imports no other Kayaka module (enforced by import-linter).

- **`core/context.py`** — a `ContextVar[str | None]` holding the current request ID, with `get/set/reset_request_id`. Shared by logging and error handling.
- **`core/middleware.py`** — three middlewares plus helpers:
  - `RequestContextMiddleware`: resolves/generates a request ID (`resolve_request_id`; accepts well-formed incoming `X-Request-ID` matching `^[A-Za-z0-9._-]{8,128}$`, otherwise generates `req_<uuid7-hex>`), stores it in the contextvar, echoes it in the response header, and writes **one access log line** per request (method, path *without* query string, status, duration, client IP) with `event="request.completed"`.
  - `TrustedProxyMiddleware`: overwrites `REMOTE_ADDR` with `X-Kayaka-Client-IP` **only** when `is_trusted_proxy_request` passes — i.e. `X-Kayaka-Proxy` matches `settings.PROXY_SHARED_SECRET` via `hmac.compare_digest` (constant-time). `X-Forwarded-For` is never trusted. IPs validated with `ipaddress`.
  - `ContentSecurityPolicyMiddleware`: adds `API_CONTENT_SECURITY_POLICY` to responses that don't already set it.
- **`core/health.py`** — `healthz` (never touches the DB) and `readyz` (runs `SELECT 1`, returns `503` + `{"checks": {"database": "error"}}` on `DatabaseError`). Both are `@never_cache` and `@transaction.non_atomic_requests` (so an unreachable DB yields 503 rather than failing to open a transaction). Not part of the OpenAPI schema.
- **`core/logging.py`** — `build_logging_config(level, fmt)`. `RequestIdFilter` injects `request_id` (or `-`) into every record. JSON formatter (`python-json-logger`) renames `asctime`→`timestamp`, `levelname`→`severity` (Google Cloud Logging-friendly); console formatter for local dev. Quiets `django.request` to ERROR (4xx already covered by the access log), `django.db.backends` and `django.server` to WARNING.
- **`core/api/views.py`** — `PingView` (`AllowAny`, no auth classes so no CSRF/session lookup). Returns service/version/environment/time with `Cache-Control: no-store`. Exposed as `ping_view = transaction.non_atomic_requests(PingView.as_view())` so ping answers without opening a DB transaction (overriding `ATOMIC_REQUESTS`).
- **`core/api/serializers.py`** — DRF serializers declared purely so they appear in the OpenAPI schema (and therefore the generated TS types): `ErrorDetailSerializer` (field/code/message), `ErrorBodySerializer` (code/message/details/`requestId` — note camelCase on the wire), `ErrorResponseSerializer`, `PingSerializer`, `PingResponseSerializer`.
- **`core/api/errors.py`** — the single error envelope implementation:
  - `error_body(code, message, details)` builds `{"error": {code, message, requestId, details?}}`, defaulting the message from `GENERIC_MESSAGES` (user-safe strings for `VALIDATION_ERROR`, `BAD_REQUEST`, `NOT_AUTHENTICATED`, `PERMISSION_DENIED`, `CSRF_FAILED`, `NOT_FOUND`, `RATE_LIMITED`, `INTERNAL_ERROR`).
  - `flatten_validation_detail` turns DRF's nested validation errors into a flat `{field, code, message}` list using dotted paths and list indexes (e.g. `variants[0].price`).
  - `exception_handler` is the DRF handler: maps `Http404`/Django `PermissionDenied` into DRF equivalents; returns `None` for non-API exceptions (so Django logs them and returns 500); upgrades DRF's 403-for-unauthenticated to a proper **401**; adds `Retry-After` for throttles; detects CSRF failures (`CSRF_FAILED`).
  - Django-level handlers `bad_request`/`permission_denied`/`not_found`/`server_error`/`csrf_failure`, plus `api_not_found` (the `/api/v1/` catch-all, also non-atomic).

Backend core tests present (per `backend/kayaka/core/tests/`): `test_smoke.py`, `test_health.py`, `test_database.py`, `test_errors.py`, `test_logging.py`, `test_middleware.py`, `test_openapi.py`, `test_ping.py`.

### 5.6 The `kayaka.accounts` module

- **`accounts/apps.py`** — `AccountsConfig`, label `accounts`.
- **`accounts/models.py`** — the **custom `User`** model, extending `AbstractBaseUser` + `PermissionsMixin`:
  - `id`: `UUIDField` primary key defaulting to **`uuid.uuid7()`** (time-ordered, non-enumerable), non-editable.
  - `email`: `EmailField(max_length=254, unique=True)`, stored lowercase.
  - `full_name`, `is_active` (default True), `is_staff` (default False), `date_joined`.
  - `USERNAME_FIELD = "email"`, `REQUIRED_FIELDS = []`.
  - `Meta.db_table = "users"` plus a `UniqueConstraint(Lower("email"), name="users_email_ci_unique")` — **case-insensitive uniqueness enforced at the database level**, catching even code paths that bypass `save()` (`bulk_create`, `update()`).
  - `clean()` and `save()` both normalize the email via `normalize_email`.
  - Docstring clarifies: identity is global; a user can belong to several tenants via memberships (Phase 2); `is_staff` only grants Django-admin access; real RBAC comes from Phase 2 tables, never these flags.
- **`accounts/managers.py`** — `normalize_email` (strip + lowercase) and `UserManager` (`use_in_migrations=True`) with case-insensitive `get_by_natural_key`, `create_user` (unusable password when `None`), and `create_superuser` (sets `is_staff`/`is_superuser`).
- **`accounts/admin.py`** — `UserAdmin` registration (list display/filters/search, no password editing — use `manage.py changepassword`). Admin is an ops tool, enabled only with `DJANGO_ADMIN_ENABLED=true`.
- **`accounts/migrations/0001_initial.py`** — creates the `users` table with the `Lower('email')` unique constraint and the custom manager. Generated by Django 5.2.17.
- **No serializers, views, URLs, or services** in `accounts` — there is **no account/auth API yet**. (Auth flows are planned via django-allauth headless in Phase 2.)

Tests: `accounts/tests/test_user_model.py` — email normalization + password hashing, UUIDv7 PK, unusable password without a password, DB-level case-insensitive uniqueness, case-insensitive authentication, superuser flags, email required, Argon2 availability.

### 5.7 Committed API contract (`backend/openapi/schema.json`)

OpenAPI 3.0.3, "Kayaka API" v1.0.0. Contains exactly one path (`/api/v1/public/ping`, `operationId: public_ping`, `security: [{}]` = public) and the shared component schemas `ErrorBody`, `ErrorDetail`, `ErrorResponse`, `Ping`, `PingResponse`. CI fails if this file (or the frontend types generated from it) drifts.

---

## 6. Frontend (`frontend/`)

### 6.1 Framework & dependencies (`package.json`)

- `kayaka-frontend` v0.1.0, `"type": "module"`, `engines.node >= 24` (`.nvmrc` = `24`).
- **Framework**: **Next.js 16.3.8** (App Router) with **React 19.3.0**.
- **Styling**: **Tailwind CSS v4.3.3** (`@tailwindcss/postcss`) + **shadcn/ui** (`components.json`, style "new-york", RSC, base color neutral, lucide icons) + `class-variance-authority`, `clsx`, `tailwind-merge`, `radix-ui`.
- **API client**: `openapi-fetch` 0.17.0 (runtime) + `openapi-typescript` 7.13.0 (dev, generates types).
- **Validation**: `zod` 4.6.5. **`server-only`** 0.0.1 guards server modules.
- **Dev/test**: TypeScript 5.9.3, ESLint 9.39.5 + `eslint-config-next`, Prettier 3.9.9, Vitest 5.0.3 + Testing Library + jsdom, Playwright 1.63.0, Vite 8.3.1.

**Scripts**: `dev`/`build`/`start`; `lint`; `format`/`format:check`; `typecheck` (`next typegen && tsc --noEmit`); `test`/`test:watch` (Vitest); `test:e2e` (Playwright); `api:generate` (openapi-typescript from `../backend/openapi/schema.json` → `src/lib/api/schema.d.ts`); `api:check` (generate + git diff).

> **Note on state management & extras:** the blueprint plans TanStack Query, Zustand, React Hook Form, Motion, Recharts, dnd-kit — **none are installed yet**. Phase 1 needs none of them, consistent with "walking skeleton."

### 6.2 Build & tooling config

- **`next.config.ts`**: `reactStrictMode`, `poweredByHeader: false`, and global security headers (`X-Content-Type-Options`, `Referrer-Policy`, `X-Frame-Options: SAMEORIGIN` — deliberately not DENY, because the dashboard will iframe-preview the storefront in Phase 7, `Permissions-Policy`) applied to all non-`/api/*` routes (Django sets its own stricter headers for the API).
- **`tsconfig.json`**: `strict`, `noUncheckedIndexedAccess`, bundler module resolution, `@/*` → `./src/*`, Next TS plugin.
- **`vitest.config.ts`**: jsdom env, tests in `tests/unit/**`, `@` alias, and a **`server-only` stub** (`tests/unit/stubs/server-only.ts`) so server modules can be unit-tested.
- **`playwright.config.ts`**: `tests/e2e`, two projects — **desktop Chrome and Pixel 7 (mobile)** — because mobile is the primary experience; starts `npm run start` unless `E2E_BASE_URL` is set; retries once in CI.
- **`eslint.config.mjs`**: extends Next core-web-vitals + TS, and encodes the **surface boundary** (ADR 0001): storefront/dashboard/admin route groups may not import each other's code via `no-restricted-imports` — shared code must live in `src/components` or `src/lib`.
- **`.env.local` validation**: `src/lib/env-schema.ts` (zod) — `API_ORIGIN` (http/https URL, trailing slashes stripped), `PROXY_SHARED_SECRET` (≥ 32 chars), `APP_ENV` enum (default `development`). `src/lib/env.ts` imports `server-only` and parses `process.env` at import time (fails the build if imported from client code).

### 6.3 The API client & proxy layer (`src/lib/api/`, `src/proxy.ts`, `src/lib/proxy-headers.ts`)

This is the heart of the frontend↔backend integration (ADR 0003 — session auth through a same-origin proxy).

- **`src/proxy.ts`** — exported `proxy(request)` (Next middleware-style) matching `/api/v1/:path*`. It rewrites the request to `serverEnv.API_ORIGIN` and attaches upstream headers. So the browser only ever talks to the Next.js origin; Next forwards to Django. No CORS, no third-party cookies.
- **`src/lib/proxy-headers.ts`** — pure, unit-tested helpers:
  - `buildUpstreamUrl` — preserves path + query on the API origin.
  - `buildUpstreamHeaders` — **deletes any client-supplied** `x-kayaka-proxy` / `x-kayaka-client-ip` (anti-spoofing), then sets the real `x-kayaka-proxy` secret, sets `x-kayaka-client-ip` when known, and preserves a well-formed `x-request-id` or generates `req_<32 hex>`.
  - `clientIpFrom` — reads `x-forwarded-for` (first entry) or `x-real-ip`, validated with `node:net`'s `isIP`.
- **`src/lib/api/schema.d.ts`** — generated TypeScript types from the backend OpenAPI schema (do not hand-edit).
- **`src/lib/api/browser.ts`** — `browserApi`: an `openapi-fetch` client with `baseUrl: ""` (relative URLs → this origin's `/api/v1/*` → proxy → Django) and `credentials: "same-origin"` (cookies).
- **`src/lib/api/server.ts`** — `serverApi`: an `openapi-fetch` client (`import "server-only"`) calling Django directly server-to-server at `serverEnv.API_ORIGIN`, attaching the proxy secret header.
- **`src/lib/api/errors.ts`** (currently the active editor file) — the client-side error model:
  - `ApiError` class (status, code, requestId, details).
  - `toApiError(status, body, requestId)` — reads the backend envelope when present (`isErrorResponse` type guard), otherwise falls back to `INTERNAL_ERROR` (≥500) or `UNEXPECTED_RESPONSE`.
  - `unwrap(call)` — awaits an openapi-fetch result, returns `data` or throws `ApiError`; network failures become `NETWORK_ERROR` with status 0.
- **`src/lib/store-slug.ts`** — `isValidStoreSlug` (regex: 3–40 chars, lowercase alphanumeric with single internal hyphens) and `storeNameFromSlug` (title-cases the slug as a placeholder display name; "The backend is authoritative in Phase 2").
- **`src/lib/utils.ts`** — `cn()` (clsx + tailwind-merge), the shadcn convention.

### 6.4 App Router structure (`src/app/`)

Root `layout.tsx` sets global metadata (title template `%s · Kayaka`), viewport, and imports `globals.css`. `globals.css` defines the shadcn/ui design-token CSS variables (oklch colors, radius, fonts) with a note that tenant storefront themes will override these per-store in a later phase, plus a `prefers-reduced-motion` block.

**Route groups (four surfaces):**

| Group | Route | Files | Behaviour today |
|---|---|---|---|
| `(marketing)` | `/` | `page.tsx` | Landing placeholder: "Kayaka" heading, tagline, server-side `<ApiStatus>` ("API connected · …"), links to the three surfaces, "Phase 1 · walking skeleton" |
| `(storefront)` | `/store/[storeSlug]` | `layout.tsx`, `page.tsx`, `loading.tsx`, `error.tsx`, plus `store/layout.tsx` (pass-through) and `store/not-found.tsx` | Mobile-first store shell. `[storeSlug]/layout.tsx` calls `notFound()` for invalid slugs **before streaming** (a real 404). `page.tsx` renders a title from the slug + 8 skeleton product cards. Everything is a placeholder; real store lookup is Phase 5 |
| `(dashboard)` | `/dashboard` | `layout.tsx`, `page.tsx`, `loading.tsx`, `error.tsx` | Responsive shell: sidebar on desktop, bottom tab bar on mobile. Nav items Home (live) + Products/Inquiries/My Store/Insights (disabled "Coming soon"). `page.tsx` shows a welcome + `<ApiStatusClient>` (browser → proxy → API). `robots: noindex` |
| `(admin)` | `/admin` | `layout.tsx`, `page.tsx`, `loading.tsx`, `error.tsx` | Dense desktop-first shell. `page.tsx` shows a 4-metric grid (all `—` placeholders) + server-side `<ApiStatus>`. `robots: noindex` |

Plus top-level `not-found.tsx` (generic 404 via `NotFoundState`) and `global-error.tsx` (last-resort boundary rendering its own `<html>`).

**Shared components (`src/components/`):**

- `ui/button.tsx` — shadcn Button via `cva` (variants: default/destructive/outline/secondary/ghost/link; sizes incl. `lg` ≥44px for mobile touch; `asChild` via Radix `Slot`).
- `ui/skeleton.tsx` — animated placeholder.
- `shared/status-badge.tsx` — accessible `role="status"` badge with `loading`/`ok`/`error` states.
- `shared/api-status.tsx` — **server component** `<ApiStatus>`: `await connection()` (never prerender), calls `serverApi` ping, shows "API connected · {version} ({environment})" or "API unreachable ({code})". `testId="api-status-server"`.
- `shared/api-status-client.tsx` — **client component** `<ApiStatusClient>`: `"use client"`, `useEffect` calls `browserApi` ping through the proxy, shows "API reachable via proxy · {version}". `testId="api-status-proxy"`.
- `shared/error-state.tsx` — shared body for `error.tsx` boundaries (never shows internal details; optional retry + digest reference).
- `shared/not-found-state.tsx` — shared 404 body with a home link.

### 6.5 Verified request paths (Phase 1)

From `docs/architecture/overview.md` and the E2E tests:

| Path | Mechanism | Proven by |
|---|---|---|
| Server component → Django | `serverApi` (openapi-fetch) with `X-Kayaka-Proxy` | home/admin show "API connected" |
| Browser → `proxy.ts` → Django | `browserApi`, relative `/api/v1/*` | dashboard status + response headers |
| Unknown API URL | Django catch-all → JSON `NOT_FOUND` | backend + E2E tests |
| Invalid store slug | `notFound()` in the store layout → `store/not-found.tsx` (real 404) | E2E |

---

## 7. Cross-cutting architecture

### 7.1 How the two halves connect

```
Browser ──▶ Next.js 16 (frontend/)
              │  proxy.ts: /api/v1/* + X-Kayaka-Proxy + X-Kayaka-Client-IP (browser calls)
              │  server components: serverApi direct to Django + X-Kayaka-Proxy
              ▼
          Django 5.2 + DRF (backend/) ──▶ PostgreSQL 17
                                       └─▶ Mailpit (dev SMTP)
```

The browser is same-origin with Next.js, so there is no CORS and cookies stay first-party. The proxy secret lets Django distinguish proxied traffic (trusted for client IP) from direct calls. The forwarded `Host` is the API's own host, so `DJANGO_ALLOWED_HOSTS` only needs the API host (original host preserved in `X-Forwarded-Host`).

### 7.2 Authentication & authorization — end to end (current vs planned)

- **Today**: DRF defaults to session auth + default-deny (`IsAuthenticated`). The custom `User` model exists with Argon2 hashing and case-insensitive email login. But **there are no login, signup, or session-issuing endpoints**, and the only live endpoint is public (`AllowAny`). So in practice nothing authenticates yet. The session/CSRF cookie machinery and the proxy secret are wired and configured.
- **Planned (Phase 2+, per ADRs & blueprint)**: django-allauth headless for auth flows; multi-tenancy via `tenant_memberships`; RBAC with permission codes and seeded roles; `/api/v1/manage/*` (tenant members, session + `X-Tenant-ID`), `/api/v1/platform/*` (platform staff), `/api/v1/auth/*`. Database isolation via PostgreSQL **Row-Level Security** with a transaction-local `app.tenant_id` set per request (why `ATOMIC_REQUESTS=True` is on now).

### 7.3 Data model & relationships

- **Current schema**: only the `users` table (custom model) plus Django's built-in `auth`, `contenttypes`, and `sessions` tables. **No tenant or business tables exist.** (Confirmed by `overview.md` and the single migration.)
- **Planned**: a shared-schema multi-tenant model (ADR 0002) with `tenants`, `tenant_memberships`, `roles`/`permissions`, `tenant_profiles`/`settings`/`features`, a **unified `orders` table** with `kind = inquiry | order` (ADR 0005), **client-side cart** (ADR 0006), **versioned JSON storefront documents** (ADR 0004), and **every product carries a default variant** (ADR 0008). Full ER diagrams are in `docs/architecture/blueprint.md §H`.

### 7.4 API conventions (`docs/development/api-conventions.md`)

- Surfaces: `/public` (none), `/manage` (session + `X-Tenant-ID`), `/platform` (session + role), `/auth` (allauth), plus infra probes. Default deny everywhere.
- Success shape: `{ "data": … }` with optional `{ "meta": { page, pageSize, total } }`.
- Error shape: the single envelope `{ "error": { code, message, details[], requestId } }` for every failure incl. 404/500. A documented HTTP-status → code table.
- Request IDs: client/proxy may supply `X-Request-ID` (8–128 of `[A-Za-z0-9._-]`), else generated; echoed in the response header, every log line, and error bodies.
- JSON keys are camelCase on the wire (automatic from Phase 2 via a camel-case renderer; hand-written in Phase 1). IDs are UUIDv7 strings; times ISO 8601 UTC; money `{ amount: <minor units>, currency }`. Every endpoint must appear in the committed OpenAPI schema or CI fails.

### 7.5 Documented architecture decisions (ADRs)

`docs/adr/` — all Accepted, dated 2026-09-30:

| # | Decision |
|---|---|
| 0001 | Modular monolith (enforced import boundaries, back and front) |
| 0002 | Shared-schema multi-tenancy with PostgreSQL RLS |
| 0003 | Session auth through a same-origin proxy (implemented in Phase 1) |
| 0004 | Versioned JSON storefront documents |
| 0005 | Unified inquiry/order model (one `orders` table) |
| 0006 | Client-side per-tenant cart for the MVP |
| 0007 | No Redis/Celery in the MVP (Django Tasks + Cloud Run Jobs) |
| 0008 | Every product has a default variant |
| 0009 | Phase 1 toolchain and exact version pins |

The blueprint (`docs/architecture/blueprint.md`) is the approved target design (v1.0, 2026-09-30) and documents 13 deliberate deviations from the original brief (e.g. one `orders` table instead of separate inquiries/orders, client cart instead of server cart, session proxy instead of JWT, Cloud Run instead of Render). The product serves personas "Charan" (platform admin), "Anjali" (entrepreneur/tenant), and "Priya" (customer), with the core loop centered on WhatsApp handoff.

---

## 8. Testing strategy

From `docs/development/testing.md` and the test files:

| Layer | Tool | Location | Command |
|---|---|---|---|
| Backend unit/API/DB | pytest + pytest-django (real Postgres) | `backend/kayaka/**/tests/` | `docker compose run --rm backend pytest` |
| Frontend unit/component | Vitest + Testing Library (jsdom) | `frontend/tests/unit/` | `npm test` |
| End-to-end | Playwright (desktop Chrome + Pixel 7) | `frontend/tests/e2e/` | `npm run build && npm run test:e2e` |

- **Backend (~52 tests)**: system checks, custom-user wiring, secure defaults (default-deny, JSON-only renderer, `NUM_PROXIES=0`, `ATOMIC_REQUESTS`), no pending migrations, health probes, DB connectivity, ping (envelope, `no-store`, security headers, no DB access, 405 envelope), error-code mapping + nested-validation flattening, middleware (request IDs, proxy trust, `X-Forwarded-For` never trusted), JSON logging, OpenAPI generation, user model. Convention: tests that need the DB must mark `@pytest.mark.django_db`; a test without the mark that touches the DB fails (proving "no DB access"). Warnings are errors.
- **Frontend (30 unit tests + 9 E2E scenarios × 2 viewports)**: env validation, proxy-header anti-spoofing/IP/request-ID logic, `ApiError` normalization, store-slug rules, shared components; E2E covers home (server→API), dashboard (browser→proxy→API with request-ID passthrough), responsive nav, storefront shell, store 404, generic 404, admin, and the proxy envelope.
- **The planned "most important suite"**: a **tenant isolation suite** that fails the build (blueprint §Q.3) — **not yet present** because tenants don't exist yet. It becomes mandatory from Phase 2.

Backend test files confirmed on disk: `core/tests/{test_smoke,test_health,test_database,test_errors,test_logging,test_middleware,test_openapi,test_ping}.py` and `accounts/tests/test_user_model.py`.

---

## 9. Implementation status: built vs partial vs missing

**Fully built (Phase 1 scope):**

- Settings split (base/dev/test/prod) with fail-fast prod validation and documented security posture.
- Custom `User` model + manager + admin + migration + tests (UUIDv7, case-insensitive unique email at the DB level, Argon2).
- Core infrastructure: JSON error envelope (DRF + Django handlers), request-ID propagation, trusted-proxy client-IP with constant-time secret compare, API CSP, structured JSON logging, `/healthz` + `/readyz`, `GET /api/v1/public/ping`.
- Committed OpenAPI schema + generated TS types, kept in sync by CI.
- Same-origin proxy with anti-spoofing header logic; typed browser + server API clients; client-side `ApiError` model.
- Four Next.js route-group shells with responsive layouts, loading/error/not-found boundaries, and live API-status checks (both server and browser paths).
- Docker Compose dev stack; multi-stage Dockerfile (dev + non-root prod gunicorn).
- Full CI (lint/format/types/boundaries/migrations/deploy-check/tests/schema-drift/secret-scan) + Dependabot.

**Partial / placeholder:**

- Dashboard and admin navigation items are rendered but disabled ("Coming soon").
- Storefront renders a title derived from the slug + skeleton cards; `storeNameFromSlug` is explicitly a placeholder until the Phase 2+ API is authoritative. Admin metrics are `—`.
- Staging deploy workflow is written and lints clean but **has never run** and depends on unprovisioned GCP/Neon/Vercel setup.
- CI itself has reportedly **never run on GitHub** (verified only locally at the time of writing). The repo now has an `origin` remote, so this may have changed since.

**Not yet implemented (planned, Phase 2+):**

- All business features: tenants, memberships, RBAC, products/variants/categories, orders/inquiries, storefront documents, cart, analytics, media pipeline, search, WhatsApp handoff, UPI payments.
- Any authentication/authorization endpoints (django-allauth headless) and the `X-Tenant-ID`-scoped `/manage` and `/platform` surfaces.
- PostgreSQL RLS and the transaction-local tenant context (the `ATOMIC_REQUESTS` groundwork is in place).
- camelCase-on-the-wire DRF renderer (hand-written for now).
- Frontend libraries named in the blueprint (TanStack Query, Zustand, React Hook Form, Motion, Recharts, dnd-kit) — none installed yet.
- The tenant isolation test suite.

---

## 10. Observations & recommendations

These are flagged for a developer picking the project up; **nothing here has been changed** (read-only investigation).

1. **A real `.env.local` exists in `frontend/`.** It holds only the dev placeholder secret and is git-ignored, so there's no leak. Still, treat it as the pattern to watch: the whole design hinges on `PROXY_SHARED_SECRET` matching on both sides and never being committed. The gitleaks CI job is the backstop.
2. **`frontend/.next/` is present in the working tree** (a local build artifact). It's git-ignored, so this is harmless, but it bloats the directory; `rm -rf frontend/.next` is safe between builds.
3. **CI/staging have not been exercised against real infrastructure.** The first real GitHub push and the first `deploy-staging` run are the true validations; `docs/development/ci.md` and `docs/development/deployment-staging.md` are the checklists to follow. Enable the recommended branch protection (`backend`, `frontend`, `e2e`, `secrets` required) once on GitHub.
4. **The discipline is the asset.** Import-linter layer/forbidden contracts, ESLint surface boundaries, strict mypy, committed lockfiles + schema, and default-deny DRF permissions are all in place now — which is exactly what makes the Phase 2 multi-tenant work safe to build. Keep every new tenant-scoped endpoint covered by the isolation suite from day one, as the testing doc insists.
5. **Watch the `ATOMIC_REQUESTS` + non-atomic exceptions.** `ping`, the health probes, and `api_not_found` are deliberately `@transaction.non_atomic_requests`. Any future endpoint that must answer without the DB (or must manage its own transaction for RLS `set_config`) needs the same treatment — this is a subtle but load-bearing pattern.
6. **Version pins are intentionally conservative** (Django 5.2 LTS, DRF 3.16, mypy < 1.20, TS < 6.1) because the 2026-09-30 ecosystem had cross-incompatibilities (ADR 0009). Don't let Dependabot bump these major lines without re-checking the compatibility matrix in that ADR.

---

### Appendix: key file index

| Area | Representative files |
|---|---|
| Backend settings | `backend/config/settings/{base,dev,test,prod}.py` |
| Backend routing | `backend/config/urls.py`, `backend/config/api_v1.py` |
| Backend core | `backend/kayaka/core/{middleware,health,logging,context}.py`, `backend/kayaka/core/api/{views,serializers,errors}.py` |
| Backend accounts | `backend/kayaka/accounts/{models,managers,admin,apps}.py`, `migrations/0001_initial.py` |
| API contract | `backend/openapi/schema.json` |
| Frontend integration | `frontend/src/proxy.ts`, `frontend/src/lib/proxy-headers.ts`, `frontend/src/lib/api/{browser,server,errors,schema.d}.ts`, `frontend/src/lib/{env,env-schema,store-slug}.ts` |
| Frontend app | `frontend/src/app/(marketing|storefront|dashboard|admin)/…`, `frontend/src/components/{ui,shared}/…` |
| Infra | `compose.yaml`, `backend/Dockerfile`, `.github/workflows/{ci,deploy-staging}.yml`, `Makefile` |
| Docs | `docs/architecture/{blueprint,overview}.md`, `docs/adr/*`, `docs/development/{api-conventions,testing,ci,local-setup,deployment-staging}.md` |

*This document reflects the repository state as read on the current branch (`main`, commit `17b9fa1`). It is a point-in-time reference; re-verify against the code after any Phase 2 work.*
