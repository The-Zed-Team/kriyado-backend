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


class DiscountSerializer(serializers.ModelSerializer):
    vendorBranch = VendorBranchSerializer(many=True, read_only=True)
    branch_ids = serializers.PrimaryKeyRelatedField(
        queryset=VendorBranch.objects.all(),
        many=True,
        write_only=True,
        source='vendorBranch'
    )

    class Meta:
        model = Discount
        fields = [
            'id',
            'vendor',
            'discount_type',
            'category',
            'value_type',
            'value',
            'description',
            'min_purchase',
            'expiry_date',
            'vendorBranch',
            'branch_ids',
            'status',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['vendor', 'status', 'created_at', 'updated_at']

    def create(self, validated_data):
        branches = validated_data.pop('vendorBranch', [])
        discount = Discount.objects.create(**validated_data)
        discount.vendorBranch.set(branches)
        return discount

    def update(self, instance, validated_data):
        branches = validated_data.pop('vendorBranch', None)
        # Any vendor edit sets discount back to pending
        instance.status = 'pending'
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if branches is not None:
            instance.vendorBranch.set(branches)
        return instance
