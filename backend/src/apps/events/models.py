import uuid

from django.db import models

from apps.common.mixins import TimestampMixin
from apps.events.enums import EventType

# Create your models here.


class Event(TimestampMixin, models.Model):
    """Model for system-wide events"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    event_type = models.CharField(
        max_length=50,
        choices=EventType.choices,
        default=EventType.PROMOTION,
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    content_id = models.CharField(max_length=100, blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "events"
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.title} ({self.start_date} - {self.end_date})"
