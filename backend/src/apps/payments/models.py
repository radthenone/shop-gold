import uuid

from django.db import models

from apps.common.mixins import TimestampMixin

# Create your models here.


class PaymentMethod(models.TextChoices):
    CREDIT_CARD = "credit_card"
    BANK_TRANSFER = "bank_transfer"
    BLIK = "blik"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class PaymentStatus(models.TextChoices):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class Payment(TimestampMixin, models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(
        "orders.Order", on_delete=models.CASCADE, related_name="payments"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20, choices=PaymentMethod.choices)
    status = models.CharField(max_length=20, choices=PaymentStatus.choices)
    transaction_id = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = "payments"
        verbose_name = "payment"
        verbose_name_plural = "payments"
