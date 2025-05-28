import uuid

from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.mixins import TimestampMixin
from apps.users.enums import Role
from apps.users.managers import UserManager

# Create your models here.


class User(AbstractBaseUser):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    email = models.EmailField(
        unique=True,
        error_messages={"unique": _("A user with this email already exists.")},
    )
    username = models.CharField(
        unique=True,
        error_messages={"unique": _("A user with this username already exists.")},
    )
    role = models.CharField(
        max_length=50,
        choices=Role.choices,
        default=Role.CUSTOMER,
    )
    password = models.CharField(max_length=255)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "users"
        verbose_name = "user"
        verbose_name_plural = "users"
        ordering = ["-date_joined"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["username"]),
        ]

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    @property
    def is_staff(self):
        return self.is_superuser

    def __str__(self):
        return f"User #{self.id}"


class Profile(TimestampMixin, models.Model):
    user = models.OneToOneField(
        "users.User",
        on_delete=models.CASCADE,
        related_name="profile",
    )
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    phone_verified = models.BooleanField(default=False)
    avatar = models.OneToOneField(
        "files.ProfileImage",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="profile_image",
    )

    objects = models.Manager()

    class Meta:
        db_table = "profiles"
        verbose_name = "profile"
        verbose_name_plural = "profiles"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Profile of {self.user.username}"

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def avatar_url(self):
        return self.avatar.image.url if self.avatar else None
