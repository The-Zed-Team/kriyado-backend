from rest_framework import serializers

from apps.shared.models import *


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ["id", "name"]


class StateSerializer(serializers.ModelSerializer):
    country_detail = CountrySerializer(read_only=True)

    class Meta:
        model = State
        fields = ("id", "name", "country_detail", "country")


class DistrictSerializer(serializers.ModelSerializer):
    state_detail = StateSerializer(read_only=True)

    class Meta:
        model = District
        fields = ("id", "name", "state", "state_detail")
