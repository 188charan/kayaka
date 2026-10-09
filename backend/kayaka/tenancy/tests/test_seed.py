"""Safety and idempotency of the seed_demo_data management command."""

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from kayaka.accounts.models import User
from kayaka.tenancy.models import Membership

PW = "seed-pass-ABCDEF-123456"


@pytest.mark.django_db
def test_requires_an_explicit_password(monkeypatch) -> None:
    monkeypatch.delenv("KAYAKA_DEMO_PASSWORD", raising=False)
    with pytest.raises(CommandError):
        call_command("seed_demo_data")


@pytest.mark.django_db
def test_refuses_non_development_environment(settings) -> None:
    settings.APP_ENV = "production"
    with pytest.raises(CommandError):
        call_command("seed_demo_data", password=PW)


@pytest.mark.django_db
def test_force_allows_non_development_environment(settings) -> None:
    settings.APP_ENV = "production"
    call_command("seed_demo_data", password=PW, force=True)
    assert User.objects.filter(email="admin@kayaka.local").exists()


@pytest.mark.django_db
def test_creates_personas_and_is_idempotent() -> None:
    call_command("seed_demo_data", password=PW)
    call_command("seed_demo_data", password=PW)  # second run must not duplicate
    assert User.objects.count() == 6  # 1 platform admin + 4 Anjali + 1 Namma
    assert User.objects.filter(email="owner@demo.kayaka.local").count() == 1
    assert Membership.objects.filter(tenant__slug="anjali-jewellery").count() == 4
    assert Membership.objects.filter(tenant__slug="namma-crafts").count() == 1
    assert User.objects.get(email="owner@demo.kayaka.local").check_password(PW)


@pytest.mark.django_db
def test_does_not_reset_existing_password_by_default() -> None:
    call_command("seed_demo_data", password=PW)
    call_command("seed_demo_data", password="a-different-password-999")
    user = User.objects.get(email="owner@demo.kayaka.local")
    assert user.check_password(PW)
    assert not user.check_password("a-different-password-999")


@pytest.mark.django_db
def test_reset_passwords_flag_updates_existing_password() -> None:
    call_command("seed_demo_data", password=PW)
    call_command("seed_demo_data", password="brand-new-password-456", reset_passwords=True)
    assert User.objects.get(email="owner@demo.kayaka.local").check_password(
        "brand-new-password-456"
    )
