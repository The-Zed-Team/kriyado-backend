from rest_framework import serializers

from apps.vendor.discounts.models import Discount, TotalBillPreset
from apps.vendor.models import VendorBranch


class TotalBillPresetSerializer(serializers.ModelSerializer):
    class Meta:
        model = TotalBillPreset
        fields = "__all__"


class DiscountSerializer(serializers.ModelSerializer):
    branches = serializers.PrimaryKeyRelatedField(
        queryset=VendorBranch.objects.all(), many=True
    )
    preset = serializers.PrimaryKeyRelatedField(
        queryset=TotalBillPreset.objects.all(), allow_null=True, required=False
    )

    class Meta:
        model = Discount
        fields = "__all__"
        read_only_fields = ["approval_status", "approved_by", "approved_at"]
