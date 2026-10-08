"""Local development settings (docker compose or a host virtualenv)."""

from kayaka.core.logging import build_logging_config

from .base import *  # noqa: F403
from .base import LOG_LEVEL, REST_FRAMEWORK, env

DEBUG = env.bool("DJANGO_DEBUG", default=True)
SECRET_KEY = env.str("DJANGO_SECRET_KEY", default="dev-only-insecure-secret-key-change-me")
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["localhost", "127.0.0.1", "backend"])
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=["http://localhost:3000"])

LOG_FORMAT = env.str("LOG_FORMAT", default="console")
LOGGING = build_logging_config(level=LOG_LEVEL, fmt=LOG_FORMAT)

# Browsable API is convenient while developing; never enabled elsewhere.
REST_FRAMEWORK = {
    **REST_FRAMEWORK,
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
}
# Browsable API and admin need inline styles/scripts.
API_CONTENT_SECURITY_POLICY = None
