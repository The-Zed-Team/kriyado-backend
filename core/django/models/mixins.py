from django.db import models


class Timestamps(models.Model):
    datetime_created = models.DateTimeField("Date created", auto_now_add=True)
    datetime_updated = models.DateTimeField("Date updated", auto_now=True)

    class Meta:
        abstract = True


class TimestampsIndexed(models.Model):
    datetime_created = models.DateTimeField(
        "Date created", auto_now_add=True, db_index=True
    )
    datetime_updated = models.DateTimeField(
        "Date updated", auto_now=True, db_index=True
    )

    class Meta:
        abstract = True
