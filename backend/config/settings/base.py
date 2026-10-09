"""Settings shared by every environment.

Environment-specific modules (dev, test, prod) import everything from here and override.
All runtime configuration comes from environment variables; nothing secret lives in code.
"""

from pathlib import Path

import environ

from kayaka.core.logging import build_logging_config

BASE_DIR = Path(__file__).resolve().parents[2]

env = environ.Env()

# ------------------------------------------------------------------ core
DEBUG = env.bool("DJANGO_DEBUG", default=False)
ALLOWED_HOSTS: list[str] = env.list("DJANGO_ALLOWED_HOSTS", default=[])
APP_ENV = env.str("APP_ENV", default="development")
APP_VERSION = env.str("APP_VERSION", default="dev")

ADMIN_ENABLED = env.bool("DJANGO_ADMIN_ENABLED", default=False)
ADMIN_URL = env.str("DJANGO_ADMIN_URL", default="django-admin/")

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",  # required by allauth
    "rest_framework",
    "drf_spectacular",
    "allauth",
    "allauth.account",
    "allauth.headless",
    "kayaka.accounts",
    "kayaka.tenancy",
]
if ADMIN_ENABLED:
    INSTALLED_APPS.insert(0, "django.contrib.admin")

SITE_ID = 1

MIDDLEWARE = [
    "kayaka.core.middleware.RequestContextMiddleware",
    "kayaka.core.middleware.TrustedProxyMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "kayaka.core.middleware.ContentSecurityPolicyMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",  # required by django-allauth
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# URLs never end with a slash (`/api/v1/public/ping`). No redirect magic.
APPEND_SLASH = False

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ------------------------------------------------------------------ database
DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default="postgres://kayaka:kayaka@localhost:5432/kayaka",
    ),
}
DATABASES["default"]["CONN_MAX_AGE"] = env.int("DATABASE_CONN_MAX_AGE", default=60)
DATABASES["default"]["CONN_HEALTH_CHECKS"] = True
# Every request runs in a transaction. Phase 2 relies on this to set the tenant context
# with transaction-local set_config() for RLS (ADR 0002).
DATABASES["default"]["ATOMIC_REQUESTS"] = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ------------------------------------------------------------------ auth
AUTH_USER_MODEL = "accounts.User"

AUTHENTICATION_BACKENDS = [
    # allauth first so email-based login works; ModelBackend kept for Django admin.
    "allauth.account.auth_backends.AuthenticationBackend",
    "django.contrib.auth.backends.ModelBackend",
]

# django-allauth, headless-only (no server-rendered allauth templates; the Next.js app drives
# the UI and talks to /_allauth/browser/v1/* through the same-origin proxy — ADR 0011).
HEADLESS_ONLY = True
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_UNIQUE_EMAIL = True
# Our User model has no username field — identity is the email (ADR 0010).
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USER_MODEL_EMAIL_FIELD = "email"
# Phase 2 has no email-sending flows wired; demo users log in directly. Verification, invites
# and password reset are added in a later phase.
ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_RATE_LIMITS = {"login_failed": "5/5m"}
# Headless config points allauth at the frontend origin for any email links it builds later.
HEADLESS_FRONTEND_URLS = {
    "account_confirm_email": "/auth/verify-email/{key}",
    "account_reset_password_from_key": "/auth/reset-password/{key}",
}

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.ScryptPasswordHasher",
]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 10},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ------------------------------------------------------------------ sessions & CSRF (ADR 0003)
SESSION_COOKIE_NAME = "kayaka_session"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_AGE = 60 * 60 * 24 * 14
CSRF_COOKIE_NAME = "kayaka_csrftoken"
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_TRUSTED_ORIGINS: list[str] = env.list("CSRF_TRUSTED_ORIGINS", default=[])
CSRF_FAILURE_VIEW = "kayaka.core.api.errors.csrf_failure"

# Shared secret the Next.js proxy attaches as X-Kayaka-Proxy. Empty disables trust.
PROXY_SHARED_SECRET = env.str("PROXY_SHARED_SECRET", default="")

# ------------------------------------------------------------------ security headers
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"
# The API only serves JSON, so nothing may be loaded or framed.
API_CONTENT_SECURITY_POLICY: str | None = "default-src 'none'; frame-ancestors 'none'"

# ------------------------------------------------------------------ i18n / time
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ------------------------------------------------------------------ static (dev admin only)
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# ------------------------------------------------------------------ email
# e.g. smtp://mailpit:1025 (dev), consolemail:// (default), smtp+tls://user:pass@host:587
_email = env.email_url("EMAIL_URL", default="consolemail://")
EMAIL_BACKEND = _email["EMAIL_BACKEND"]
EMAIL_HOST = _email.get("EMAIL_HOST", "")
EMAIL_PORT = _email.get("EMAIL_PORT") or 25
EMAIL_HOST_USER = _email.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = _email.get("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = _email.get("EMAIL_USE_TLS", False)
EMAIL_USE_SSL = _email.get("EMAIL_USE_SSL", False)
EMAIL_TIMEOUT = 10
DEFAULT_FROM_EMAIL = env.str("DEFAULT_FROM_EMAIL", default="Kayaka <no-reply@localhost>")
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# ------------------------------------------------------------------ DRF
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    # Default deny: public endpoints must opt in with AllowAny.
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "kayaka.core.api.errors.exception_handler",
    # Never trust X-Forwarded-For directly; TrustedProxyMiddleware sets REMOTE_ADDR.
    "NUM_PROXIES": 0,
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Kayaka API",
    "DESCRIPTION": "Multi-tenant commerce platform API. See docs/development/api-conventions.md.",
    # Contract version, not the app build version, so the committed schema is deterministic.
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SCHEMA_PATH_PREFIX": r"/api/v1",
}

# ------------------------------------------------------------------ logging
LOG_LEVEL = env.str("LOG_LEVEL", default="INFO")
LOG_FORMAT = env.str("LOG_FORMAT", default="json")
LOGGING = build_logging_config(level=LOG_LEVEL, fmt=LOG_FORMAT)
