# API conventions

These apply to every endpoint from Phase 1 on. The full endpoint plan is in
[blueprint §R](../architecture/blueprint.md#r-api-specification).

## Surfaces

| Prefix | Who | Auth | Notes |
|---|---|---|---|
| `/api/v1/public/…` | Anyone (storefront) | None | Read-mostly, cacheable |
| `/api/v1/manage/…` | Tenant members | Session + `X-Tenant-ID` | Phase 2+ |
| `/api/v1/platform/…` | Platform staff | Session + platform role | Phase 2+ |
| `/api/v1/auth/…` | Everyone | allauth headless | Phase 2+ |
| `/healthz`, `/readyz` | Infrastructure | None | Not part of the OpenAPI schema |

**Default deny:** DRF's default permission is `IsAuthenticated`. Public endpoints must opt in
explicitly with `AllowAny`.

## Success responses

```json
{ "data": { "…": "…" } }
{ "data": [ … ], "meta": { "page": 1, "pageSize": 20, "total": 134 } }
```

## Error responses

Every error, including 404s for unknown URLs and 500s, uses one envelope:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Some fields need attention.",
    "details": [{ "field": "email", "code": "invalid", "message": "Enter a valid email address." }],
    "requestId": "req_0199a1b2c3d4…"
  }
}
```

| HTTP | `code` |
|---|---|
| 400 | `VALIDATION_ERROR`, `BAD_REQUEST` |
| 401 | `NOT_AUTHENTICATED` |
| 403 | `PERMISSION_DENIED`, `CSRF_FAILED` |
| 404 | `NOT_FOUND` (also used for other tenants' resources) |
| 405 | `METHOD_NOT_ALLOWED` |
| 406 | `NOT_ACCEPTABLE` |
| 415 | `UNSUPPORTED_MEDIA_TYPE` |
| 429 | `RATE_LIMITED` (+ `Retry-After`) |
| 500 | `INTERNAL_ERROR` (never exposes internals) |

Domain errors subclass DRF's `APIException` with a `default_code`. The handler upper-cases it
into `code` (for example `product_not_active` → `PRODUCT_NOT_ACTIVE`).

## Request IDs

- The client or proxy may send `X-Request-ID` (8–128 chars of `[A-Za-z0-9._-]`). Anything else
  is replaced by a generated `req_<uuid7-hex>`.
- The ID is echoed in the `X-Request-ID` response header, included in every log line, and
  returned as `requestId` in error bodies.

## Client IP and the proxy

See [ADR 0003](../adr/0003-session-auth-same-origin-proxy.md). Django uses
`X-Kayaka-Client-IP` only when `X-Kayaka-Proxy` matches `PROXY_SHARED_SECRET`.

## Other rules

- JSON keys are **camelCase** on the wire (automatic from Phase 2; hand-written in Phase 1).
- IDs are UUID strings (UUIDv7). Times are ISO 8601 UTC.
- Money is `{ "amount": <minor units>, "currency": "INR" }`.
- Every endpoint must appear in the OpenAPI schema (`backend/openapi/schema.json`). CI fails if
  the committed schema or the generated frontend types are stale.
