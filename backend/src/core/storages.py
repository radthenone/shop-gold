import io
import mimetypes
import os
from datetime import timedelta

from django.conf import settings
from django.core.files.base import ContentFile
from PIL import Image
from storages.backends.s3boto3 import S3Boto3Storage


class DefaultStorage(S3Boto3Storage):
    endpoint_url = settings.AWS_S3_ENDPOINT_URL  # http://minio:9000
    bucket_name = ""
    custom_domain = settings.AWS_S3_CUSTOM_DOMAIN.rstrip("/")

    @property
    def custom_domain_with_bucket(self):  # localhost:9000/static/
        domain = self.custom_domain
        bucket = self.bucket_name.strip("/")
        return f"{domain}/{bucket}/"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if settings.USE_AWS:
            self.custom_domain = f"{self.custom_domain}/"
        else:
            self.custom_domain = self.custom_domain_with_bucket


class PublicStorage(DefaultStorage):
    default_acl = "public-read"
    file_overwrite = True
    secure_urls = False
    use_ssl = False
    url_protocol = "http:"

    @property
    def querystring_auth(self):
        return False


class PublicStorageExpire(DefaultStorage):
    default_acl = "public-read"
    file_overwrite = True
    secure_urls = False
    use_ssl = False
    url_protocol = "http:"
    querystring_expire = timedelta(minutes=10).total_seconds()

    @property
    def querystring_auth(self):  # if true, the url will be signed and will expire
        return True


class PrivateStorage(DefaultStorage):
    default_acl = "private"
    file_overwrite = False
    secure_urls = False
    use_ssl = False
    url_protocol = "http:"

    @property
    def querystring_auth(self):
        return False


class StaticStorage(PublicStorage):
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    location = ""  # file folder name


class ProfileStorage(PublicStorage):
    bucket_name = "profiles"
    location = ""  # root directory in bucket


class ProductStorage(PublicStorage):
    bucket_name = "products"
    location = ""  # root directory in bucket


#
# class BaseImageStorage(S3Boto3Storage):
#     def _save(self, name, content):
#         if self._is_image(name) and self.get_target_size():
#             image = Image.open(content)
#             target_size = self.get_target_size()
#             image = image.resize(target_size, Image.Resampling.LANCZOS)
#
#             buffer = io.BytesIO()
#             image.save(buffer, format="WEBP")
#             buffer.seek(0)
#
#             new_name = self._normalize_name(name)
#             if not new_name.lower().endswith(".webp"):
#                 new_name = f"{os.path.splitext(new_name)[0]}.webp"
#
#             return super()._save(new_name, ContentFile(buffer.read()))
#         else:
#             return super()._save(name, content)
#
#     @staticmethod
#     def _is_image(name):
#         image_extensions = (".jpg", ".jpeg", ".png", ".gif", ".bmp")
#         return name.lower().endswith(image_extensions)
#
#     def get_mime_type(self):
#         """Subclasses must define mime_type like image/jpeg"""
#         raise NotImplementedError("Subclasses must define mime_type")
#
#     def get_target_size(self) -> tuple[int, int]:
#         """Subclasses must define target_size like (100, 100)"""
#         raise NotImplementedError("Subclasses must define target_size")
#
#     @staticmethod
#     def get_object_id(name):
#         return name.split("/")[0]
#
#     def set_object_key(self, name):
#         _id = self.get_object_id(name)
#         return f"{_id}/{name}"
#
#     def set_content_type(self, name):
#         if self._is_image(name):
#             return self.get_mime_type()
#         else:
#             mime_type, _ = mimetypes.guess_type(name)
#             return mime_type or "application/octet-stream"
#
#     def get_object_parameters(self, name):
#         params = super().get_object_parameters(name)
#         params["Key"] = self.set_object_key(name)
#         params["ContentType"] = self.set_content_type(name)
#         return params
#
#
# class StaticStorage(PublicStorage):
#     location = ""  # file folder name
#     bucket_name = "static"  # bucket name
#
#
# class ProfileImageStorage(BaseImageStorage, PublicStorage):
#     location = ""
#     bucket_name = "profiles"
#     endpoint_url = settings.AWS_S3_ENDPOINT_URL  # http://minio:9000
#     custom_domain = (
#         f"{settings.AWS_S3_CUSTOM_DOMAIN}/{bucket_name}/"  # localhost:9000/static/
#     )
#
#     def get_target_size(self):
#         return 200, 200
#
#     def get_mime_type(self):
#         return "image/webp"
#
#
# class ProductImageStorage(BaseImageStorage):
#     bucket_name = "products"
#     location = "images"
#     file_overwrite = False
#     default_acl = "public-read"
#
#     def get_target_size(self):
#         return 500, 500
#
#     def get_mime_type(self):
#         return "image/webp"
#
#
# class PublicMediaStorage(S3Boto3Storage):
#     bucket_name = "media"
#     location = "media"
#     default_acl = "public-read"
#     file_overwrite = True
#     custom_domain = f"{settings.AWS_S3_ENDPOINT_URL}/{bucket_name}/"
#     url_protocol = "http:"
#
#     @property
#     def querystring_auth(self):
#         return False
#
#
# class PrivateMediaStorage(S3Boto3Storage):
#     location = "private"
#     default_acl = "private"
#     file_overwrite = False
#
#     @property
#     def querystring_auth(self):  # if true, the url will be signed and will expire
#         return True
