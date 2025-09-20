# from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

# # from services import *
from apps.account.models import User
from apps.vendor.models import Vendor

# # from validator import *


# class UserRegisterSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True, validators=[validate_password])
#     confirm_password = serializers.CharField(
#         write_only=True, validators=[ConfirmPasswordValidator()]
#     )

#     class Meta:
#         model = User
#         fields = ["email", "password", "confirm_password"]

#     def create(self, validated_data):
#         email = validated_data["email"]
#         password = validated_data["password"]

#         return UserService.register_user(email=email, password=password)


class UserInfoSerializer(serializers.ModelSerializer):
    has_vendor_account = serializers.SerializerMethodField()
    has_customer_account = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "phone_number",
            "first_name",
            "middle_name",
            "last_name",
            "auth_provider",
            "email_verified",
            "phone_verified",
            "has_vendor_account",
            "has_customer_account",
        ]

    def get_has_vendor_account(self, obj):
        return Vendor.objects.filter(user=obj).exists()

    def get_has_customer_account(self, obj):
        # customer account status fetching not implemented
        return False
