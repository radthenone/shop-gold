from django.urls import URLPattern, URLResolver, include, path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# router.register(r"", AccountViewSet, basename="user")

urlpatterns: list[URLPattern | URLResolver] = [
    # path("", include(router.urls)),
]
