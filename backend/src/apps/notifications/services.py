import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings

from apps.notifications.models import Notification, NotificationToken

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Service for sending notifications to users.
    """

    @classmethod
    def send_push(cls, user_id, title, message, data=None):
        """
        Send a push notification to a user.

        Args:
            user_id: The ID of the user to send the notification to
            title: The title of the notification
            message: The message content of the notification
            data: Additional data to include with the notification (dict)

        Returns:
            The created notification object
        """
        from django.contrib.auth import get_user_model

        User = get_user_model()

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            logger.error(f"Failed to send notification: User {user_id} not found")
            return None

        # Create notification record
        notification = Notification.objects.create(
            user=user,
            title=title,
            message=message,
            data=data or {},
            notification_type=data.get("type", "info") if data else "info",
        )

        # Send to all active tokens for this user
        tokens = NotificationToken.objects.filter(user=user, is_active=True)

        # If we have WebSocket channels set up, send through them
        if hasattr(settings, "CHANNEL_LAYERS") and settings.CHANNEL_LAYERS:
            try:
                channel_layer = get_channel_layer()

                # Send to user's group
                async_to_sync(channel_layer.group_send)(
                    f"user_{user.id}",
                    {
                        "type": "notification.message",
                        "notification": {
                            "id": str(notification.id),
                            "title": title,
                            "message": message,
                            "data": data or {},
                            "created_at": notification.created_at.isoformat(),
                            "type": data.get("type", "info") if data else "info",
                        },
                    },
                )
                logger.info(f"WebSocket notification sent to user {user.id}")
            except Exception as e:
                logger.error(f"Failed to send WebSocket notification: {e!s}")

        # Log for debugging
        logger.info(f"Notification sent to user {user.id}: {title}")

        return notification

    @classmethod
    def send_mfa_code(cls, user_id, code, method="app"):
        """
        Send an MFA code to a user via the app.

        Args:
            user_id: The ID of the user to send the code to
            code: The MFA code
            method: The method used for MFA (app, email, etc.)

        Returns:
            The created notification object
        """
        title = "Authentication Code"
        message = f"Your MFA code is: {code}"
        data = {"type": "mfa_code", "code": code, "method": method}

        return cls.send_push(user_id, title, message, data)
