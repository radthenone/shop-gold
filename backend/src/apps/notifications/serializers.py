from rest_framework import serializers

from apps.notifications.models import Notification, NotificationToken


class NotificationTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationToken
        fields = ("id", "token", "device_type", "is_active", "created_at")
        read_only_fields = ("id", "created_at")


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = (
            "id",
            "title",
            "message",
            "data",
            "is_read",
            "notification_type",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
