from django.db.models.signals import pre_save
from django.dispatch import receiver

from apps.files.models import ProductImage, ProfileImage
from core.utils import add_image_path


@receiver(pre_save, sender=ProfileImage)
def set_avatar_path(sender, instance, **kwargs):
    if not instance.image.name.startswith(str(instance.profile.user.id)):
        instance.image.name = add_image_path(instance.profile.user.id, "avatar")


@receiver(pre_save, sender=ProductImage)
def set_product_image_path(sender, instance, **kwargs):
    if not instance.image.name.startswith(str(instance.product.id)):
        instance.image.name = add_image_path(
            instance.product.id, f"image_{instance.order}"
        )
