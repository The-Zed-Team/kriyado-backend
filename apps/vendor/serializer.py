from rest_framework import serializers

from services import *


class VendorProfileSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = VendorProfile
        fields = '__all__'

    def create(self, validated_data):
        return create_vendor_profile(validated_data)


class VendorBranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorBranch
        exclude = ['vendor']


class VendorDiscountSerializer(serializers.ModelSerializer):
    branches = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=VendorBranch.objects.all(),
        required=False
    )

    class Meta:
        model = VendorDiscount
        exclude = ['vendor']
