"""Staging and production settings. Every value without a safe default is required."""

from .base import *  # noqa: F403
from .base import env

DEBUG = False
APP_ENV = env.str("APP_ENV")  # "staging" or "production"
SECRET_KEY = env.str("DJANGO_SECRET_KEY")  # required: fails fast if missing
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS")
PROXY_SHARED_SECRET = env.str("PROXY_SHARED_SECRET")

if len(PROXY_SHARED_SECRET) < 32:
    raise ValueError("PROXY_SHARED_SECRET must be at least 32 characters")

# TLS terminates at the platform (Cloud Run); it forwards the original scheme.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# No redirect: Cloud Run only serves HTTPS publicly, and internal probes use plain HTTP.
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=60 * 60 * 24 * 365)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = False
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SILENCED_SYSTEM_CHECKS = [
    "security.W008",  # SECURE_SSL_REDIRECT intentionally off (see above)
    "security.W021",  # HSTS preload is hard to undo; enable once the production domain is final
]
