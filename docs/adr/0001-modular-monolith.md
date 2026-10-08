# 0001. Modular monolith

- Status: Accepted
- Date: 2026-09-30

## Context

Kayaka is built by a single developer on free-tier infrastructure. The domain has clear
sub-areas (tenancy, catalog, orders, storefront, analytics, …) that will grow at different
speeds, and some may one day need to scale or deploy independently. Microservices would add
network calls, distributed transactions, multiple deploy pipelines, and service discovery,
with no benefit at current scale.

## Decision

- The backend is **one Django project, deployed as one container**, organised into modules
  (Django apps) under the `kayaka` package: `core`, `accounts`, and later `access`, `tenants`,
  `media`, `catalog`, `customers`, `orders`, `storefront`, `messaging`, `analytics`, `audit`,
  `platform`, `promotions`, `payments`.
- Modules are **created only when the phase that needs them starts**. No empty placeholders.
- Inside a module: `models`, `selectors` (reads), `services` (writes/use cases), `api/`
  (serializers + views per surface), `tests/`. No repository layer; the ORM is enough.
- **Boundary rule:** a module may import another module's `services`, `selectors`, `types`,
  and `events` only. It never imports another module's `models` or `api`. `core` is the
  lowest layer and imports no other Kayaka module.
- Boundaries are enforced in CI with `import-linter` (contracts in `backend/pyproject.toml`).
  Contracts are extended as modules are added.
- The frontend is **one Next.js app** with separate route groups for the storefront,
  tenant dashboard, and platform admin.

## Consequences

- One deploy, one database transaction boundary, simple local development.
- Extraction to a service later is possible because cross-module calls already go through
  explicit service/selector functions.
- Discipline is needed. `import-linter` catches forbidden imports, but good module design
  still depends on code review.

## Alternatives considered

- **Microservices:** rejected. Operational cost far exceeds benefit at this stage.
- **Unstructured monolith:** rejected. It becomes hard to reason about, and hard to split later.
