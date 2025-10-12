from rest_framework import serializers

from apps.vendor.discounts.models import DiscountPreset, VendorBranchDiscount, Category
from apps.vendor.models import VendorBranch


class VendorBranchDiscountSerializer(serializers.ModelSerializer):
    preset = serializers.PrimaryKeyRelatedField(
        queryset=DiscountPreset.objects.all(), allow_null=True, required=False
    )
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), allow_null=True, required=False
    )
    discount_value = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False
    )
    purchase_above = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False
    )

    def validate(self, attrs):
        if "preset" in attrs and attrs["preset"] is not None:
            if (
                attrs.get("purchase_above") is not None
                or attrs.get("discount_value") is not None
            ):
                raise serializers.ValidationError(
                    {
                        "non_field_errors": "Cannot set purchase_above or discount_value when preset is selected."
                    }
                )
            preset = attrs["preset"]
            attrs["purchase_above"] = preset.purchase_above
            attrs["discount_value"] = preset.discount_value
            attrs["category"] = preset.category
        elif attrs["type"] == "category_based":
            if "category" not in attrs or attrs["category"] is None:
                raise serializers.ValidationError(
                    {"category": "This field is required for category type discounts."}
                )
        return super().validate(attrs)

    def create(self, validated_data):
        validated_data["vendor_branch"] = self.context["request"].vendor_branch
        return super().create(validated_data)

    class Meta:
        model = VendorBranchDiscount
        fields = (
            "id",
            "name",
            "type",
            "description",
            "preset",
            "purchase_above",
            "discount_value",
            "category",
            "approval_status",
            "approved_by",
            "status",
        )
        read_only_fields = ["approval_status", "approved_by", "status"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "description")
        read_only_fields = ["id"]


class DiscountPresetSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), allow_null=True, required=False
    )

    def validate(self, attrs):
        if attrs["type"] == "category_based":
            if "category" not in attrs or attrs["category"] is None:
                raise serializers.ValidationError(
                    {"category": "This field is required for category type discounts."}
                )
        if "preset" in attrs and attrs["preset"] is not None:
            if (
                attrs.get("purchase_above") is not None
                or attrs.get("discount_value") is not None
            ):
                raise serializers.ValidationError(
                    {
                        "non_field_errors": "Cannot set purchase_above or discount_value when preset is selected."
                    }
                )
            preset = attrs["preset"]
            attrs["purchase_above"] = preset.purchase_above
            attrs["discount_value"] = preset.discount_value
            attrs["category"] = preset.category
        return super().validate(attrs)

    class Meta:
        model = DiscountPreset
        fields = (
            "id",
            "name",
            "type",
            "description",
            "purchase_above",
            "discount_value",
            "category",
        )
        read_only_fields = ["id"]


# class TotalBillPresetSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TotalBillPreset
#         fields = "__all__"


# class DiscountSerializer(serializers.ModelSerializer):
#     branches = serializers.PrimaryKeyRelatedField(
#         queryset=VendorBranch.objects.all(), many=True
#     )
#     preset = serializers.PrimaryKeyRelatedField(
#         queryset=TotalBillPreset.objects.all(), allow_null=True, required=False
#     )

#     class Meta:
#         model = Discount
#         fields = "__all__"
#         read_only_fields = ["approval_status", "approved_by", "approved_at"]
