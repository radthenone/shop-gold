from django.db import models


class EventType(models.TextChoices):
    PROMOTION = "promotion", "Promotion Event"
    SALE = "sale", "Sale Event"
    MAINTENANCE = "maintenance", "Maintenance"
    NEW_FEATURE = "new_feature", "New Feature"
    HOLIDAY = "holiday", "Holiday Event"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]
