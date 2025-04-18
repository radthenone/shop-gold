import logging

from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)


class NotificationConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.user_group_name = None
        self.user = None

    async def connect(self):
        await self.accept()
        self.user = self.scope["user"]

        if self.user.is_anonymous:
            await self.close()
            return

        # Add user to their own group
        await self.channel_layer.group_add(f"user_{self.user.id}", self.channel_name)

        # Add user to the broadcast group
        await self.channel_layer.group_add("broadcast", self.channel_name)

        logger.info("WebSocket connection established for user %s", self.user.id)

    async def disconnect(self, close_code):
        if hasattr(self, "user_group_name"):
            await self.channel_layer.group_discard(
                self.user_group_name, self.channel_name
            )
            await self.channel_layer.group_discard("broadcast", self.channel_name)

        logger.info(
            "WebSocket connection closed for user %s",
            self.user.id if not self.user.is_anonymous else "anonymous",
        )
