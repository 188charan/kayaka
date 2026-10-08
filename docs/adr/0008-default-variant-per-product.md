# 0008. Every product has a default variant

- Status: Accepted
- Date: 2026-09-30

## Context

Most MVP products have a single price and stock level. Later, tenants need options such as size
or colour, each with its own price and stock. Moving price and stock from products to variants
after launch would require a data migration and changes across the catalog, pricing, inquiry,
and analytics code.

## Decision

- **Price and stock always live on `product_variants`.**
- Every product has **at least one variant**. The first is `is_default = true` (enforced by a
  partial unique index).
- The dashboard hides variants when a product has only the default one. The product form edits
  the default variant's price and stock directly.
- Order items and cart entries always reference a **variant ID**.

## Consequences

- Adding options and variants later is a UI change, not a data migration.
- Every product read joins or prefetches variants, which is slightly more work in queries and
  serializers.

## Alternatives considered

- **Price and stock on `products`, variants added later:** simpler today, but an expensive
  migration later.
