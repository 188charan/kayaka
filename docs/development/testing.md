# Testing

| Layer | Tool | Location | Command |
|---|---|---|---|
| Backend unit/API/DB | pytest + pytest-django (real PostgreSQL) | `backend/kayaka/**/tests/` | `docker compose run --rm backend pytest` |
| Frontend unit/component | Vitest + Testing Library (jsdom) | `frontend/tests/unit/` | `npm test` |
| End-to-end | Playwright (desktop Chrome + Pixel 7) | `frontend/tests/e2e/` | `npm run build && npm run test:e2e` |

## What Phase 1 covers

**Backend (52 tests)**
- Smoke: Django system checks, custom user model wiring, secure defaults (default-deny permissions,
  JSON-only renderer, `NUM_PROXIES=0`, `ATOMIC_REQUESTS`), no pending migrations.
- Health: `/healthz` never touches the DB; `/readyz` returns 200 or 503 when the DB is down.
- Database connectivity: PostgreSQL ≥ 17 and a parameterised round trip.
- Ping: data envelope, `Cache-Control: no-store`, security headers, no DB access, 405 envelope.
- Errors: every error class maps to the documented code; nested validation errors flatten
  to dotted paths; internals are never exposed; unknown API URLs return the envelope.
- Middleware: request ID generation/acceptance/rejection; trusted-proxy client IP only with the
  correct secret; `X-Forwarded-For` never trusted.
- Logging: JSON lines carry `severity`, `timestamp`, and `request_id`.
- OpenAPI: schema generates, includes shared components, excludes probes.
- Users: email normalisation, UUIDv7 IDs, case-insensitive uniqueness enforced by the DB,
  case-insensitive login, Argon2 available.

**Frontend (30 unit tests, 9 E2E scenarios × 2 viewports)**
- Env validation, proxy header logic (anti-spoofing, client IP, request IDs), API error
  normalisation, store slug rules, shared components.
- E2E: home (server → API), dashboard (browser → proxy → API), responsive navigation,
  storefront shell, store 404, generic 404, admin, proxy envelope and request-ID passthrough.

## Conventions

- Tests that need the database say so (`@pytest.mark.django_db`). A test without the mark that
  touches the DB fails, which is how "no DB access" is proven.
- Warnings are errors in pytest (`filterwarnings = error`).
- Every new tenant-scoped endpoint from Phase 2 on must be covered by the **tenant isolation
  suite** (blueprint §Q.3). It is the most important test suite in the repo.
- E2E tests run on both desktop and mobile viewports. Mobile is the primary experience.
