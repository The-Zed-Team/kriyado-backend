from rest_framework import serializers

from apps.customer.models import *


class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = "__all__"


class DurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Duration
        fields = "__all__"
