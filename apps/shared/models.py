import uuid

from django.db import models


class Country(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = "country"

    def __str__(self):
        return self.name


class State(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, related_name="states"
    )

    class Meta:
        db_table = "state"
        unique_together = ("name", "country")

    def __str__(self):
        return f"{self.name}, {self.country.name}"


class District(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name="districts")

    class Meta:
        db_table = "district"
        unique_together = ("name", "state")

    def __str__(self):
        return f"{self.name}, {self.state.name}"
