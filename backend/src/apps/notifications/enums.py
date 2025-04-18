from django.db import models


class NotificationType(models.TextChoices):
    MFA_CODE = "mfa_code", "MFA Code"
    DELIVERY_STATUS = "delivery_status", "Delivery Status"
    EVENT = "event", "Event"
    INFO = "info", "Info"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]
