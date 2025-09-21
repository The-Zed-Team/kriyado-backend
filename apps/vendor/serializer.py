import re

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


# class VendorProfileSerializer(serializers.ModelSerializer):
#     user = serializers.HiddenField(default=serializers.CurrentUserDefault())

#     class Meta:
#         model = VendorProfile
#         fields = '__all__'

#     def create(self, validated_data):
#         return create_vendor_profile(validated_data)


# class VendorBranchSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = VendorBranch
#         exclude = ['vendor']


# class VendorDiscountSerializer(serializers.ModelSerializer):
#     branches = serializers.PrimaryKeyRelatedField(
#         many=True,
#         queryset=VendorBranch.objects.all(),
#         required=False
#     )

#     class Meta:
#         model = VendorDiscount
#         exclude = ['vendor']


class VendorBranchSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = VendorBranch
        fields = (
            "id",
            "country",
            "state",
            "district",
            "shop_locality",
            "nearby_town",
            "pin_code",
            "key_person_name",
            "key_person_contact_number",
            "land_phone",
        )

    def validate_key_person_contact_number(self, value):
        """
        Validate that the contact number is numeric and 10 digits long.
        """
        # Allow only digits
        if not re.match(r"^\d{10}$", value):
            raise serializers.ValidationError("Enter a valid 10-digit mobile number.")
        return value

    def create(self, validated_data):
        vendor = Vendor.objects.get(user=self.context["user"])
        validated_data["vendor"] = vendor
        return super().create(validated_data)


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
