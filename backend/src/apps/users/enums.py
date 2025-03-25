from django.db import models


class Role(models.TextChoices):
    ADMIN = "admin"
    CUSTOMER = "customer"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]
