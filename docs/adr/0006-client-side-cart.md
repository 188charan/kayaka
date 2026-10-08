# 0006. Client-side per-tenant cart for MVP

- Status: Accepted
- Date: 2026-09-30

## Context

Customers browse anonymously. Server-side carts for anonymous users need session tracking,
cleanup jobs, and frequent writes to a small free-tier database, and give no MVP benefit because
checkout is a WhatsApp inquiry.

## Decision

- The cart lives in the browser (Zustand + `persist`), keyed **per tenant**
  (`kayaka:cart:{tenantId}`), so carts from different stores never mix on a shared device.
- The cart stores only `{variantId, qty, addedAt}`. **Prices are never trusted from the
  client.** The server re-prices at display time (`POST /cart/price`) and at inquiry creation.
- The inquiry request carries only variant IDs and quantities. The server validates that every
  variant belongs to the store's tenant and is active.
- `ADD_TO_CART` / `REMOVE_FROM_CART` are still recorded as analytics events.

## Consequences

- No cart tables, no cleanup jobs, and the cart works offline.
- Carts don't sync across devices, and there's no abandoned-cart recovery.
- Server-side carts can be introduced with customer accounts without changing the inquiry API.

## Alternatives considered

- **Server carts keyed by anonymous session:** rejected for MVP (cost and complexity without benefit).
