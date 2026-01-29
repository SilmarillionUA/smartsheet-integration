import uuid

from django.conf import settings
from django.db import models


class Sheet(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sheets",
    )
    smartsheet_id = models.BigIntegerField()
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["user", "smartsheet_id"]
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
