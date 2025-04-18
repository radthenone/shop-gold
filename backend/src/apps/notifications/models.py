import uuid

from django.db import models

from apps.common.mixins import TimestampMixin
from apps.notifications.enums import NotificationType


class NotificationToken(TimestampMixin, models.Model):
    """
    Model to store notification tokens for users.
    These tokens are used to identify devices for push notifications.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="notification_tokens",
    )
    token = models.CharField(max_length=255, unique=True)
    device_type = models.CharField(
        max_length=20,
        choices=[
            ("web", "Web"),
            ("android", "Android"),
            ("ios", "iOS"),
        ],
        default="web",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "notification_tokens"
        verbose_name = "notification token"
        verbose_name_plural = "notification tokens"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Token for {self.user.email} ({self.device_type})"


class Notification(TimestampMixin, models.Model):
    """
    Model to store notifications sent to users.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    data = models.JSONField(default=dict, blank=True)
    is_read = models.BooleanField(default=False)
    notification_type = models.CharField(
        max_length=50,
        choices=NotificationType.choices,
        default=NotificationType.INFO,
    )

    class Meta:
        db_table = "notifications"
        verbose_name = "notification"
        verbose_name_plural = "notifications"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Notification for {self.user.email}: {self.title}"
