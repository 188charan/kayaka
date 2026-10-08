# 0009. Phase 1 toolchain and version pins

- Status: Accepted
- Date: 2026-09-30

## Context

Phase 1 fixes the toolchain every later phase builds on. Some ecosystem versions current on
2026-09-30 are incompatible with each other, and the developer machine has Docker and Node but
not `uv`, `pnpm`, or a modern Python.

## Decision

| Area | Choice | Reason |
|---|---|---|
| Python | 3.14 (container image `python:3.14.7-slim-trixie`) | Current stable; stdlib `uuid.uuid7()` for time-ordered IDs |
| Django | 5.2.17 LTS | Approved; supported until April 2028 |
| DRF | 3.16.1 | Supports Django 5.2. Its stubs (3.16.9) pair with `django-stubs` 5.2.9. The DRF 3.17+ stubs require Django 6 stubs. |
| mypy | 1.19.1 | `django-stubs` 5.2.9 supports mypy < 1.20 |
| Python packaging | `uv` (0.12.21) with a committed `uv.lock` | Fast, reproducible, one tool |
| Backend runtime in dev | Docker Compose | The host needs no Python; the same image family is used everywhere |
| Node | 24 LTS in CI (`engines: >=24`) | Active LTS; local Node 26 also works |
| JS package manager | **npm** (not pnpm as the blueprint suggested) | pnpm isn't installed and Node ≥ 25 no longer bundles corepack. npm keeps setup to zero extra tools for a single developer. |
| TypeScript | 5.9.3 | TS 7.0 is npm's default now, but `typescript-eslint` requires < 6.1 and `openapi-typescript` requires ^5 |
| ESLint | 9.39.x | `eslint-plugin-react`/`import`/`jsx-a11y` don't support ESLint 10 yet |
| Next.js | 16.3.8 | App Router, `proxy.ts` |
| Tailwind | 4.3.3 | CSS-variable theming |
| Postgres | 17.11 | Same major version as the planned Neon deployment |
| JSON on the wire | Envelope keys written in camelCase by hand in Phase 1 | The camelCase DRF renderer is added in Phase 2, when real serializers appear |

All dependencies are pinned exactly (`==` in `pyproject.toml`, exact versions in
`package.json`, lockfiles committed). GitHub Actions are pinned by commit SHA. Dependabot
proposes upgrades weekly.

## Consequences

- Upgrading to Django 6.x LTS (6.2, expected April 2027) also moves DRF and the stubs forward.
  That upgrade is planned for the hardening phase.
- Contributors need only Docker and Node 24+ to run everything. `uv` on the host is optional
  (for IDE integration).

## Alternatives considered

- **Django 6.1 now:** newer, but not LTS and not what was approved.
- **pnpm via `npm i -g pnpm`:** workable, but an extra global tool for little gain in a single-app repo.
