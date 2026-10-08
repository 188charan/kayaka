# 0005. Unified inquiry/order model

- Status: Accepted
- Date: 2026-09-30

## Context

The default checkout is a WhatsApp inquiry. Some tenants will later accept online payment. Two
separate tables (`inquiries`, `orders`) would duplicate items, statuses, customer links, inbox UI,
and analytics, and would need a migration when a tenant enables payments.

## Decision

- One `orders` table with `kind = 'inquiry' | 'order'`, plus `order_items` (immutable price
  snapshots) and `order_status_events` (timeline).
- Business status (`new → contacted → confirmed → completed | cancelled`) is separate from
  `payment_status` (`not_required | pending | paid | failed | refunded`).
- Per-tenant sequential numbers from `tenant_counters` give references such as `KY-1042`.
- The UI still uses the word "Inquiries" for tenants who don't take payments.
- MVP creates only `kind = 'inquiry'` records. Payments are out of the initial implementation.

## Consequences

- One inbox, one analytics source of truth, and no data migration when payments arrive.
- Some columns (payment status, shipping address) are unused for inquiry-only tenants.

## Alternatives considered

- **Separate `inquiries` and `orders`:** clearer names, but duplicated logic and a conversion step.
