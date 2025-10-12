import uuid
from django.db import models


class AbstractPermission(models.Model):
    """
    An abstract base class model that provides permission fields.
    """

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True, db_index=True
    )
    code = models.CharField(max_length=100, unique=True, null=False, blank=False)
    name = models.CharField(max_length=255, null=False, blank=False)
    description = models.CharField(max_length=500, null=True, blank=True)
    data = models.JSONField(
        blank=True,
        null=True,
        help_text="Additional data for the permission (e.g., description, metadata).",
    )

    class Meta:
        abstract = True
