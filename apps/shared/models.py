import uuid

from django.db import models

from core.django.models.mixins import Timestamps


class Country(Timestamps):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = "country"

    def __str__(self):
        return self.name


class State(Timestamps):
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


class District(Timestamps):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name="districts")

    class Meta:
        db_table = "district"
        unique_together = ("name", "state")

    def __str__(self):
        return f"{self.name}, {self.state.name}"


# class Address(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
#     country = models.ForeignKey(Country, on_delete=models.PROTECT)
#     state = models.ForeignKey(State, on_delete=models.PROTECT)
#     district = models.ForeignKey(District, on_delete=models.PROTECT)
#     city = models.CharField(max_length=100)
#     nearby_landmark = models.CharField(max_length=255, blank=True, null=True)
#     pin_code = models.CharField(max_length=10)


#     class Meta:
#         db_table = "address"

#     def __str__(self):
#         return f"{self.address_line1}, {self.city}, {self.state}, {self.country} - {self.postal_code}"
