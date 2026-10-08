# Local setup

## Prerequisites

| Tool | Version | Why |
|---|---|---|
| Docker Desktop (or Docker Engine + Compose v2) | Compose ≥ 2.20 | Runs Postgres, Mailpit, and the Django backend |
| Node.js | 24 LTS or newer (`frontend/.nvmrc`) | Runs the Next.js frontend |
| Git | any | |

You don't need Python on your machine. The backend, its tests, and its tools run inside the
backend container. Installing [uv](https://docs.astral.sh/uv/) is optional (only for editor
integration; see the end of this page).

## First run

```bash
git clone <repo-url> kayaka
cd kayaka

# 1. Backend stack: Postgres + Mailpit + Django (migrations run automatically)
docker compose up --build --wait

# 2. Frontend (in a second terminal)
cd frontend
cp .env.example .env.local
npm ci
npm run dev
```

Open:

| URL | What |
|---|---|
| http://localhost:3000 | Frontend (shows "API connected" when the backend is up) |
| http://localhost:3000/dashboard | Tenant dashboard shell (calls the API through the proxy) |
| http://localhost:3000/store/demo-store | Storefront shell |
| http://localhost:3000/admin | Platform admin shell |
| http://localhost:8000/api/v1/docs | Swagger UI (dev only) |
| http://localhost:8000/healthz, /readyz | Backend probes |
| http://localhost:8000/django-admin/ | Django admin (dev only; create a superuser first) |
| http://localhost:8025 | Mailpit inbox (all dev email lands here) |

`docker compose up` without `--wait` streams logs in the foreground. With `--wait` it returns
once every service is healthy; follow logs with `docker compose logs -f backend`.

## Everyday commands

The `Makefile` has shortcuts for all of these.

```bash
# Backend: run anything inside the backend container
docker compose run --rm backend python manage.py createsuperuser
docker compose run --rm backend python manage.py makemigrations
docker compose run --rm backend python manage.py sendtestemail you@example.com  # → Mailpit
docker compose run --rm backend bash

# Backend checks (same as CI)
docker compose run --rm backend sh -c 'ruff check . && ruff format --check . && lint-imports && mypy .'
docker compose run --rm backend pytest

# Frontend checks (same as CI)
cd frontend
npm run lint && npm run format:check && npm run typecheck && npm test && npm run build

# E2E smoke tests (backend must be up; uses a production build)
npx playwright install chromium   # first time only
npm run build && npm run test:e2e
```

## Changing the API contract

The OpenAPI schema is committed, and the frontend types are generated from it. CI fails if
either is stale.

```bash
make schema
# which runs:
docker compose run --rm -T backend python manage.py spectacular --settings config.settings.test \
  --format openapi-json --validate --fail-on-warn --file openapi/schema.json
cd frontend && npm run api:generate
```

## Configuration

- Root `.env` (optional, copy from `.env.example`) overrides compose values such as ports and
  the proxy secret.
- `frontend/.env.local` (copy from `frontend/.env.example`) holds the frontend's server-side
  settings, validated at startup. **`PROXY_SHARED_SECRET` must match on both sides.**
- Never commit real secrets. `.env*` files are git-ignored except the examples.

## Resetting

```bash
docker compose down        # stop, keep data
docker compose down -v     # stop and delete the database volume
docker compose build --no-cache backend   # after changing backend dependencies
```

## Troubleshooting

| Symptom | Fix |
|---|---|
| `port is already allocated` | Set `POSTGRES_PORT`, `BACKEND_PORT`, … in a root `.env` (and `API_ORIGIN` in `frontend/.env.local`) |
| Frontend shows "API unreachable (NETWORK_ERROR)" | Backend not running: `docker compose ps`, `docker compose logs backend` |
| Frontend fails to start with "Invalid environment configuration" | Create `frontend/.env.local` from `.env.example` |
| New Python dependency not found | `docker compose build backend` (dependencies are baked into the image) |

## Optional: backend tooling on the host (editor integration)

```bash
brew install uv            # or see https://docs.astral.sh/uv/
cd backend && uv sync      # creates backend/.venv with Python 3.14
```

Point your editor's Python interpreter at `backend/.venv`. Running the backend on the host also
works: set `DATABASE_URL=postgres://kayaka:kayaka@localhost:5432/kayaka`, then
`uv run python manage.py runserver`.
