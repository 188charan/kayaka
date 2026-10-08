# 0007. No Redis/Celery in the MVP

- Status: Accepted
- Date: 2026-09-30

## Context

Background work in the MVP is small: an email on a new inquiry, cache revalidation calls,
hourly analytics rollups, and daily cleanup. Redis + Celery would need an always-on worker and a
Redis instance. Neither has a free tier worth depending on, and they add operational surface.

## Decision

- **No Redis, Celery, Kafka, or other brokers in the MVP.**
- Short post-commit work (email, revalidation) runs in `transaction.on_commit` with tight timeouts.
  Failures are logged and never fail the user's request.
- Scheduled work runs as Django management commands executed by **Cloud Run Jobs** triggered by
  **Cloud Scheduler** (GitHub Actions `schedule` as a fallback). Jobs are idempotent.
- Queued work, when first needed (bulk imports, exports), uses the **Django Tasks API** via the
  `django-tasks` database backend, so a move to Celery/Redis later is a backend swap.
- Caching and throttling use Django's database/local-memory cache backends until a shared cache
  is proven necessary (then Upstash Redis).

## Consequences

- Zero extra infrastructure, and one fewer thing to learn and monitor.
- Work is minute-level, not real-time. Retries for post-commit work are limited until the
  task queue arrives.

## Alternatives considered

- **Celery + Redis:** rejected for now. Revisit when sub-minute async at volume is needed.
- **Procrastinate / django-q2:** viable, but the Django Tasks API keeps us closer to core Django.
