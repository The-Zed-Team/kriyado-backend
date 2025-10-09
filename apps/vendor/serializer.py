from rest_framework import serializers

from apps.vendor.models import *


class CreateVendorSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    shop_type = serializers.PrimaryKeyRelatedField(
        queryset=ShopType.objects.all(), required=True
    )

    def validate(self, attrs):
        if Vendor.objects.filter(user=self.context["user"]).exists():
            raise serializers.ValidationError(
                "Vendor profile already exists for this user."
            )
        return super().validate(attrs)

    def create(self, validated_data):
        user = self.context["user"]
        validated_data["user"] = user
        return super().create(validated_data)

    class Meta:
        model = Vendor
        fields = (
            "id",
            "name",
            "contact_number",
            "shop_type",
            "business_type",
            "owner_name",
        )


class UpdateVendorSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    shop_type = serializers.PrimaryKeyRelatedField(
        queryset=ShopType.objects.all(), required=False
    )

    def validate(self, attrs):
        vendor = getattr(self.instance, "user", None)
        if vendor and vendor != self.context["user"]:
            raise serializers.ValidationError(
                "You cannot update another user's vendor profile."
            )
        return super().validate(attrs)

    class Meta:
        model = Vendor
        fields = (
            "id",
            "name",
            "contact_number",
            "shop_type",
            "business_type",
            "owner_name",
        )
        read_only_fields = ("id",)


class ShopTypeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = ShopType
        fields = (
            "id",
            "name",
            "code",
            "description"
        )


class VendorDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = (
            "id",
            "name",
            "contact_number",
            "shop_type",  # FK to ShopType
            "business_type",
            "owner_name",
            "is_onboarded",
            "profile",  # OneToOne to VendorProfile
            "branches",  # reverse FK to VendorBranch
        )
        depth = 2  # expands profile, default_branch inside profile, branches, shop_type



class VendorBranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorBranch
        fields = "__all__"


class TotalBillPresetSerializer(serializers.ModelSerializer):
    class Meta:
        model = TotalBillPreset
        fields = "__all__"


class DiscountSerializer(serializers.ModelSerializer):
    branches = serializers.PrimaryKeyRelatedField(queryset=VendorBranch.objects.all(), many=True)
    preset = serializers.PrimaryKeyRelatedField(queryset=TotalBillPreset.objects.all(), allow_null=True, required=False)

    class Meta:
        model = Discount
        fields = "__all__"
        read_only_fields = ["approval_status", "approved_by", "approved_at"]
