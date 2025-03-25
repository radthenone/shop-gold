from django.core.validators import RegexValidator
from django.db import models

# Create your models here.


class DeliveryAddress(models.Model):
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="delivery_address",
    )
    address = models.TextField()
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)

    class Meta:
        db_table = "delivery_addresses"
        verbose_name = "delivery_address"
        verbose_name_plural = "delivery_addresses"

    def __str__(self):
        return f"DeliveryAddress #{self.id}"


class DeliveryPhone(models.Model):
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="delivery_phone",
    )
    phone = models.CharField(
        max_length=16,
        null=True,
        blank=True,
        validators=[
            RegexValidator(
                regex=r"^\+?1?\d{9,15}$",
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.",
            )
        ],
    )
    verified = models.BooleanField(default=False)

    class Meta:
        db_table = "delivery_phones"
        verbose_name = "delivery_phone"
        verbose_name_plural = "delivery_phones"

    def __str__(self):
        return f"DeliveryPhone #{self.id}"
