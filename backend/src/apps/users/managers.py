from typing import TYPE_CHECKING

from django.contrib.auth.models import BaseUserManager
from django.db import transaction

from apps.users.enums import Role

if TYPE_CHECKING:
    from apps.users.models import User


class UserManager(BaseUserManager):
    def unique_email(self, email: str) -> bool:
        email = self.normalize_email(email)
        return not self.filter(email=email).exists()

    def unique_username(self, username: str) -> bool:
        return not self.filter(username=username).exists()

    def is_superuser(self, email: str) -> bool:
        return self.filter(email=email, is_superuser=True).exists()

    @transaction.atomic
    def _create_user(
        self, email: str, username: str, password: str, **extra_fields
    ) -> "User":
        if not email:
            raise ValueError("User must have an email address")
        if not username:
            raise ValueError("User must have a username")
        if not password:
            raise ValueError("User must have a password")

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            username=username,
            **extra_fields,
        )
        user.set_password(password)
        user.save()
        return user

    def create_user(
        self,
        email: str,
        username: str,
        password: str,
        **extra_fields,
    ) -> "User":
        extra_fields.setdefault("role", Role.CUSTOMER)
        return self._create_user(email, username, password, **extra_fields)

    def create_superuser(
        self, email: str, username: str, password: str, **extra_fields
    ) -> "User":
        extra_fields.setdefault("role", Role.ADMIN)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self._create_user(email, username, password, **extra_fields)
