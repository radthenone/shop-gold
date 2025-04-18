from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.notifications.views import NotificationTokenViewSet, NotificationViewSet

router = DefaultRouter()
router.register(r"notifications", NotificationViewSet, basename="notification")
router.register(r"tokens", NotificationTokenViewSet, basename="notification-token")

urlpatterns = [
    path("", include(router.urls)),
]
