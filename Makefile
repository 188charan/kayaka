# Convenience shortcuts. Each target is a plain command you can also run yourself
# (see docs/development/local-setup.md). Backend commands run inside the backend container.
.PHONY: up down logs backend-shell backend-check backend-test schema frontend-check e2e check

BACKEND = docker compose run --rm -T backend

up:            ## start db, mailpit and backend
	docker compose up --build --detach --wait

down:          ## stop the stack (data is kept in the pgdata volume)
	docker compose down

logs:
	docker compose logs --follow backend

backend-shell:
	docker compose run --rm backend bash

backend-check: ## lint, format, boundaries, types, migrations
	$(BACKEND) sh -c 'ruff check . && ruff format --check . && lint-imports && mypy . && python manage.py makemigrations --check --dry-run --settings config.settings.test'

backend-test:
	$(BACKEND) pytest

schema:        ## regenerate the OpenAPI schema and the frontend API types
	$(BACKEND) python manage.py spectacular --settings config.settings.test --format openapi-json --validate --fail-on-warn --file openapi/schema.json
	cd frontend && npm run api:generate

frontend-check:
	cd frontend && npm run lint && npm run format:check && npm run typecheck && npm test && npm run build

e2e:           ## requires `make up` and a built frontend (`npm run build`)
	cd frontend && npm run test:e2e

check: backend-check backend-test frontend-check e2e
