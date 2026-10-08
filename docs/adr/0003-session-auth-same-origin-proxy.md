# 0003. Session authentication through a same-origin proxy

- Status: Accepted
- Date: 2026-09-30

## Context

The frontend (Next.js on Vercel) and the API (Django on Cloud Run) live on different origins.
Browser auth options: JWTs stored in JS-readable storage (XSS can steal them), or cookies
(cross-site cookies are increasingly blocked, especially by Safari, and require CORS with credentials).

## Decision

- The browser talks **only to the Next.js origin**. Next's `proxy.ts` forwards
  `/api/v1/*` to Django. From the browser's point of view the API is same-origin,
  so there is no CORS and there are no third-party cookies.
- Authentication uses **Django sessions** (`HttpOnly; Secure; SameSite=Lax` cookie) with
  Django's **CSRF** protection on unsafe methods. Auth flows come from django-allauth headless
  (Phase 2).
- The proxy **overwrites** two headers on every forwarded request:
  - `X-Kayaka-Proxy: <shared secret>`
  - `X-Kayaka-Client-IP: <client IP as seen by the edge>`
- Django trusts `X-Kayaka-Client-IP` **only** when `X-Kayaka-Proxy` matches the shared secret
  (constant-time compare). Otherwise the socket address is used. DRF is configured with
  `NUM_PROXIES = 0`, so `X-Forwarded-For` is never trusted directly.
- Server components call Django directly (server-to-server), sending the same secret.
- A future mobile app uses allauth's token ("app") client against the same endpoints.

## Consequences

- Session cookies can't be read by JavaScript, and there's no token refresh logic.
- Every dashboard API call passes through the proxy, which adds a small latency and one Vercel
  function invocation per call (well within the free tier).
- The shared secret must be kept in sync between the frontend and backend environments.
- Direct calls to the Cloud Run URL still work, but aren't trusted for client IP and get
  stricter throttles (Phase 2).

## Alternatives considered

- **JWT in localStorage:** rejected (XSS token theft, refresh complexity).
- **Cookies on a shared parent domain (`app.` / `api.`):** viable, but requires the custom domain
  before anything works and still needs CORS. It can be adopted later without backend changes.
- **Static `next.config` rewrites:** can't attach the secret or client IP headers.
