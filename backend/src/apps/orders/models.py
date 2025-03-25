from django.db import models


class OrderStatus(models.TextChoices):
    PENDING = "pending"
    PAID = "paid"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    RETURNED = "returned"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


# Create your models here.


class Order(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="orders"
    )
    status = models.CharField(
        max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING
    )
    tax_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment = models.ForeignKey(
        "payments.Payment",
        on_delete=models.CASCADE,
        related_name="orders",
    )
    paid_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)
    is_delivered = models.BooleanField(default=False)

    class Meta:
        db_table = "orders"
        verbose_name = "order"
        verbose_name_plural = "orders"

    def __str__(self):
        return f"Order #{self.id}"


class OrderItem(models.Model):
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(
        "orders.Order", on_delete=models.CASCADE, related_name="order_item"
    )
    product = models.ForeignKey(
        "shop.Product", on_delete=models.CASCADE, related_name="order_item"
    )
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = "order_items"
        verbose_name = "order_item"
        verbose_name_plural = "order_items"

    def __str__(self):
        return f"OrderItem #{self.id}"
