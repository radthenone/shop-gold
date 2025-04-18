from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.notifications.models import Notification, NotificationToken
from apps.notifications.serializers import (
    NotificationSerializer,
    NotificationTokenSerializer,
)


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user notifications.
    """

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=False, methods=["post"])
    def mark_all_read(self, request):
        """Mark all notifications as read"""
        self.get_queryset().update(is_read=True)
        return Response({"detail": "All notifications marked as read"})

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        """Mark a specific notification as read"""
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({"detail": "Notification marked as read"})


class NotificationTokenViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing notification tokens.
    """

    serializer_class = NotificationTokenSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return NotificationToken.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["post"])
    def register_token(self, request):
        """Register a new device token"""
        token = request.data.get("token")
        device_type = request.data.get("device_type", "web")

        if not token:
            return Response(
                {"detail": "Token is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Check if token already exists
        existing_token = NotificationToken.objects.filter(token=token).first()
        if existing_token:
            # If token exists but belongs to another user, update it
            if existing_token.user != request.user:
                existing_token.user = request.user
                existing_token.device_type = device_type
                existing_token.is_active = True
                existing_token.save()
            # If token exists and belongs to this user, just make sure it's active
            elif not existing_token.is_active:
                existing_token.is_active = True
                existing_token.save()

            serializer = self.get_serializer(existing_token)
            return Response(serializer.data)

        # Create new token
        serializer = self.get_serializer(
            data={"token": token, "device_type": device_type}
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
