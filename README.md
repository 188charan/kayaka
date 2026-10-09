# Kayaka

A multi-tenant commerce platform for small entrepreneurs: each business gets its own
persistent, searchable, customizable storefront, and customers send inquiries on WhatsApp.

**Status:** Phase 2 (identity, access & tenancy) complete — authentication, tenants, memberships,
permission-code RBAC and PostgreSQL row-level security. No business features yet.

## Quick start

Requires Docker (Compose v2) and Node.js 24+.

```bash
git clone <repo-url> kayaka && cd kayaka
docker compose up --build --wait          # Postgres + Mailpit + Django on :8000

cd frontend
cp .env.example .env.local
npm ci
npm run dev                               # Next.js on :3000
```

Open http://localhost:3000. It should say **API connected**. Full instructions, commands, and
troubleshooting: [docs/development/local-setup.md](docs/development/local-setup.md).

## Repository layout

```
backend/     Django 5.2 + DRF modular monolith (config/, kayaka/core, kayaka/accounts)
frontend/    Next.js 16 app: storefront, tenant dashboard, platform admin route groups
docs/        architecture blueprint, ADRs, development guides
compose.yaml local development stack
.github/     CI, staging deploy (manual), Dependabot
```

## Documentation

- [Architecture blueprint](docs/architecture/blueprint.md) — the approved target design
- [Architecture overview](docs/architecture/overview.md) — what exists today
- [Architecture decisions (ADRs)](docs/adr/README.md)
- [API conventions](docs/development/api-conventions.md)
- [Identity, access & tenancy](docs/development/identity-and-tenancy.md) — auth, RBAC, tenant
  context and RLS (Phase 2)
- [Demo accounts & personas](docs/development/demo-accounts.md) — local dev personas, seeding
  and login
- [Testing](docs/development/testing.md) · [CI](docs/development/ci.md) ·
  [Staging deployment](docs/development/deployment-staging.md)
