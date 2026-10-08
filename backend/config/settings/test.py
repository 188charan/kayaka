"""Test settings (pytest, CI, mypy's django plugin)."""

from kayaka.core.logging import build_logging_config

from .base import *  # noqa: F403
from .base import env

DEBUG = False
SECRET_KEY = "test-only-insecure-secret-key"
ALLOWED_HOSTS = ["testserver", "localhost"]
APP_ENV = "test"
APP_VERSION = "test"
PROXY_SHARED_SECRET = "test-proxy-secret-0123456789abcdef"

# Fast hashing in tests only.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

LOG_LEVEL = env.str("LOG_LEVEL", default="WARNING")
LOGGING = build_logging_config(level=LOG_LEVEL, fmt="json")
