from django.urls import URLPattern, URLResolver, include, path
from rest_framework.routers import DefaultRouter

from apps.auth.views import AuthViewSet, TotpViewSet

router = DefaultRouter()
router.register(r"", AuthViewSet, basename="auth")
router.register(r"totp", TotpViewSet, basename="totp")

urlpatterns: list[URLPattern | URLResolver] = [
    path("", include(router.urls)),
]
