"""Backend smoke tests: the project boots and its configuration is sane."""

import pytest
from django.apps import apps
from django.conf import settings
from django.core.management import call_command


def test_django_system_checks_pass():
    call_command("check", fail_level="WARNING")


def test_custom_user_model_is_configured():
    assert settings.AUTH_USER_MODEL == "accounts.User"
    assert apps.get_model(settings.AUTH_USER_MODEL)._meta.db_table == "users"


def test_secure_defaults():
    rf = settings.REST_FRAMEWORK
    assert rf["DEFAULT_PERMISSION_CLASSES"] == ["rest_framework.permissions.IsAuthenticated"]
    assert rf["DEFAULT_RENDERER_CLASSES"] == ["rest_framework.renderers.JSONRenderer"]
    assert rf["NUM_PROXIES"] == 0
    assert settings.SESSION_COOKIE_HTTPONLY is True
    assert settings.X_FRAME_OPTIONS == "DENY"
    assert settings.DATABASES["default"]["ATOMIC_REQUESTS"] is True


@pytest.mark.django_db
def test_no_pending_migrations():
    call_command("makemigrations", "--check", "--dry-run", verbosity=0)
