from django.core.validators import MinValueValidator
from django.db import models

# Create your models here.


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        db_table = "categories"
        verbose_name = "category"
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self):
        return f"Category #{self.id}"


class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    category = models.ForeignKey(
        "shop.Category",
        on_delete=models.CASCADE,
        related_name="products",
    )
    images = models.ForeignKey(
        "files.ProductImage",
        on_delete=models.CASCADE,
        related_name="product_images",
        null=True,
        blank=True,
    )
    description = models.TextField()
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
        ],
        help_text="Price must be greater than or equal to 0",
    )
    stock = models.PositiveIntegerField(default=0)
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "products"
        verbose_name = "product"
        verbose_name_plural = "products"
        ordering = ["name", "-created"]

    def __str__(self):
        return f"Product #{self.id}"


def images_urls(self):
    return [image.url() for image in self.images.all()]
