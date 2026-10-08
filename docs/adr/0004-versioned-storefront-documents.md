# 0004. Versioned JSON storefront documents

- Status: Accepted
- Date: 2026-09-30

## Context

Tenants customise their storefront: theme tokens and an ordered list of configurable
sections. They need draft editing, preview, publish, and rollback. A future visual builder will
edit the same data.

## Decision

- Each tenant's storefront configuration is a **single JSON document per revision**
  (`storefront_revisions.document`), with `schemaVersion` on the document and `v` on each section.
- `storefronts` points at one mutable **draft** revision and one **published** revision.
  Publishing creates an immutable revision. Rollback copies an old revision into the draft, and
  that draft is then published.
- Documents are validated by **JSON Schema files** (single source of truth in
  `packages/storefront-schema/`). The backend validates with `jsonschema` and runs referential
  checks (every referenced asset, category, and product belongs to the tenant). The frontend
  generates TypeScript types from the same files.
- Sections **reference** data (sources such as `flag`, `category`, `manual`); they never embed
  prices or product copies. Links are typed targets; images are the tenant's own asset IDs.
- **Upcasters** (pure functions, `v1 → v2`) live only in the backend, so the frontend
  renderer only knows the latest shapes. Unknown section types are skipped, never crash.
- Draft saves use optimistic concurrency (`If-Match` / `ETag`).

## Consequences

- Publish and rollback are atomic and trivial; preview renders exactly what will go live.
- There are no database FKs from documents to products, so integrity relies on validation at
  save/publish time plus a tolerant renderer.
- Schema evolution needs upcasters and fixture tests.

## Alternatives considered

- **`storefront_pages` + `storefront_sections` rows:** relational integrity, but versioning,
  preview, and rollback become multi-row copy operations, and builder state no longer maps 1:1.
