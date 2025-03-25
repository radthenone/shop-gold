from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from core.storages import ProductStorage, ProfileStorage


class Image(models.Model):
    id = models.AutoField(primary_key=True)
    image = models.ImageField(storage=None, upload_to="")
    created = models.DateTimeField(auto_now_add=True)
    order = models.PositiveIntegerField(default=0)

    # Generic models relations
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        abstract = True
        ordering = ["order", "created"]
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

    def __str__(self):
        return f"Image #{self.id}"

    def url(self):
        return self.image.url if self.image else None


class ProfileImage(Image):
    image = models.ImageField(
        storage=ProfileStorage(),
        upload_to="",
    )

    class Meta:
        db_table = "profile_images"
        verbose_name = "profile_image"
        verbose_name_plural = "profile_images"

    def __str__(self):
        return f"ProfileImage #{self.id}"


class ProductImage(Image):
    image = models.ImageField(
        storage=ProductStorage(),
        upload_to="",
    )

    class Meta:
        db_table = "product_images"
        verbose_name = "product_image"
        verbose_name_plural = "product_images"

    def __str__(self):
        return f"ProductImage #{self.id}"
