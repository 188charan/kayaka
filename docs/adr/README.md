# Architecture Decision Records

Each ADR records one significant decision: the context, what we decided, and what it costs us.
ADRs are immutable once accepted. To change a decision, write a new ADR that supersedes the old one.

| # | Title | Status |
|---|---|---|
| [0001](0001-modular-monolith.md) | Modular monolith | Accepted |
| [0002](0002-postgres-rls-multi-tenancy.md) | Shared-schema multi-tenancy with PostgreSQL RLS | Accepted |
| [0003](0003-session-auth-same-origin-proxy.md) | Session authentication through a same-origin proxy | Accepted |
| [0004](0004-versioned-storefront-documents.md) | Versioned JSON storefront documents | Accepted |
| [0005](0005-unified-inquiry-order-model.md) | Unified inquiry/order model | Accepted |
| [0006](0006-client-side-cart.md) | Client-side per-tenant cart for MVP | Accepted |
| [0007](0007-no-redis-celery-in-mvp.md) | No Redis/Celery in the MVP | Accepted |
| [0008](0008-default-variant-per-product.md) | Every product has a default variant | Accepted |
| [0009](0009-phase-1-toolchain.md) | Phase 1 toolchain and version pins | Accepted |
| [0010](0010-rbac-and-tenant-context.md) | Permission-code RBAC and the Phase 2 tenant-context mechanism | Accepted |
| [0011](0011-allauth-headless-via-proxy.md) | django-allauth headless through the same-origin proxy | Accepted |

## Template

```markdown
# NNNN. Title

- Status: Proposed | Accepted | Superseded by NNNN
- Date: YYYY-MM-DD

## Context
What forces are at play? What problem are we solving?

## Decision
What we will do.

## Consequences
What becomes easier, what becomes harder, what we must watch.

## Alternatives considered
What we rejected and why.
```
