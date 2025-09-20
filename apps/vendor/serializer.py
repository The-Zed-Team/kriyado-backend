from rest_framework import serializers

from apps.vendor.models import ShopType, Vendor


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
