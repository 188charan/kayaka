from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.contrib.auth.base_user import BaseUserManager

if TYPE_CHECKING:
    from kayaka.accounts.models import User


def normalize_email(email: str) -> str:
    """Emails are stored lowercase, so lookups and uniqueness are case-insensitive."""
    return email.strip().lower()


class UserManager(BaseUserManager["User"]):
    use_in_migrations = True

    def get_by_natural_key(self, username: str | None) -> User:
        return self.get(email=normalize_email(username or ""))

    def create_user(self, email: str, password: str | None = None, **extra: Any) -> User:
        if not email:
            raise ValueError("Users must have an email address")
        extra.setdefault("is_staff", False)
        extra.setdefault("is_superuser", False)
        user = self.model(email=normalize_email(email), **extra)
        user.set_password(password)  # None -> unusable password
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str | None = None, **extra: Any) -> User:
        extra["is_staff"] = True
        extra["is_superuser"] = True
        return self.create_user(email, password, **extra)
