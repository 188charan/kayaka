import pytest
from django.contrib.auth import authenticate, get_user_model
from django.db import IntegrityError, transaction
from django.test import override_settings

User = get_user_model()

pytestmark = pytest.mark.django_db


def test_create_user_normalises_email_and_hashes_password():
    user = User.objects.create_user("  Anjali@Example.COM ", password="a-strong-pass-123")
    assert user.email == "anjali@example.com"
    assert user.password != "a-strong-pass-123"
    assert user.check_password("a-strong-pass-123")
    assert not user.is_staff
    assert not user.is_superuser


def test_primary_key_is_uuid7():
    user = User.objects.create_user("a@example.com")
    assert user.pk.version == 7


def test_user_without_password_cannot_log_in():
    user = User.objects.create_user("nopass@example.com")
    assert not user.has_usable_password()


def test_email_uniqueness_is_case_insensitive_at_database_level():
    User.objects.create_user("dup@example.com")
    with pytest.raises(IntegrityError), transaction.atomic():
        # bypass save() normalisation to prove the DB constraint itself holds
        User.objects.bulk_create([User(email="DUP@example.com")])


def test_authenticate_by_email_is_case_insensitive():
    User.objects.create_user("login@example.com", password="a-strong-pass-123")
    user = authenticate(username="LOGIN@Example.com", password="a-strong-pass-123")
    assert user is not None
    assert user.email == "login@example.com"


def test_create_superuser_sets_flags():
    admin = User.objects.create_superuser("root@example.com", password="a-strong-pass-123")
    assert admin.is_staff
    assert admin.is_superuser


def test_create_user_requires_email():
    with pytest.raises(ValueError, match="email"):
        User.objects.create_user("")


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.Argon2PasswordHasher"])
def test_argon2_hasher_is_available():
    user = User.objects.create_user("argon@example.com", password="a-strong-pass-123")
    assert user.password.startswith("argon2")
