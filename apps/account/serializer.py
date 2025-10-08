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


class SuperUserCreateSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    phone_number = serializers.CharField(required=False)
    password = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    middle_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        if not attrs.get("email") and not attrs.get("phone_number"):
            raise serializers.ValidationError("Email or phone number is required")
        return attrs

    def create(self, validated_data):
        return User.objects.create_superuser(**validated_data)
