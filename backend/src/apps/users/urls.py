from django.urls import URLPattern, URLResolver, include, path
from rest_framework.routers import DefaultRouter

from apps.users.views import (
    AccountViewSet,
    TOTPViewSet,
)

router = DefaultRouter()
router.register(r"", AccountViewSet, basename="user")
router.register(r"totp", TOTPViewSet, basename="totp")

urlpatterns: list[URLPattern | URLResolver] = [
    path("", include(router.urls)),
]
