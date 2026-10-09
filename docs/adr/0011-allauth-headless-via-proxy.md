# 0011. django-allauth headless through the same-origin proxy

- Status: Accepted
- Date: 2026-10-09
- Refines: [0003](0003-session-auth-same-origin-proxy.md) (names the auth implementation it
  anticipated)

## Context

ADR 0003 chose Django sessions + CSRF behind a same-origin Next.js proxy, and noted "auth flows
come from django-allauth headless (Phase 2)". This ADR records how allauth is wired.

## Decision

- Add **django-allauth** with `allauth`, `allauth.account`, `allauth.headless` and
  `django.contrib.sites`. Run **`HEADLESS_ONLY = True`**: allauth serves no server-rendered
  templates; the Next.js app owns all UI and talks to the headless JSON API.
- Login method is **email + password** (`ACCOUNT_LOGIN_METHODS = {"email"}`). Email
  verification, invites and password reset are deferred to a later phase
  (`ACCOUNT_EMAIL_VERIFICATION = "none"` for now).
- The browser calls allauth's **browser client** endpoints under `/_allauth/browser/v1/*`
  (session-based). The Next.js proxy forwards both `/api/v1/*` and `/_allauth/*` to Django, so
  these are same-origin to the browser (no CORS, no third-party cookies).
- **CSRF**: unsafe requests send `X-CSRFToken` echoing the readable `kayaka_csrftoken` cookie.
  The SPA fetches `GET /api/v1/auth/csrf` to prime the cookie. CSRF is never disabled and
  `@csrf_exempt` is never used.
- Our own identity/tenancy surface stays in DRF under `/api/v1/` (`/me`, `/tenants`, …) with the
  standard error envelope and OpenAPI types. allauth owns only the auth transitions
  (login/logout/session).

## Consequences

- No bespoke auth code: allauth handles password hashing policy, rate limiting, and the session
  lifecycle; we inherit future flows (verification, reset, MFA) without re-architecting.
- allauth's headless responses use allauth's own JSON shape, which differs from our envelope.
  That boundary is isolated to the auth endpoints; everything else uses our contract.
- `django.contrib.sites` with `SITE_ID = 1` is required.
- A future mobile app can use allauth's token ("app") client against the same backend.

## Alternatives considered

- **Hand-rolled session login endpoint**: fewer moving parts now, but we'd reimplement rate
  limiting, verification, reset and MFA later. Rejected.
- **allauth with templates (non-headless)**: conflicts with the Next.js-owned UI. Rejected.
- **JWT / token auth in the browser**: rejected by ADR 0003 (XSS risk).
