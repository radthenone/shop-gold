from django.urls import URLPattern, URLResolver, include, path
from rest_framework.routers import DefaultRouter

from apps.users.views import AccountViewSet

router = DefaultRouter()
router.register(r"users", AccountViewSet, basename="user")

urlpatterns: list[URLPattern | URLResolver] = [
    path("", include(router.urls)),
]
