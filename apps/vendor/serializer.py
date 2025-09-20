from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from apps.account.models import User
from apps.account.services import UserService
from apps.vendor.validator import ConfirmPasswordValidator


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, validators=[ConfirmPasswordValidator()])

    class Meta:
        model = User
        fields = ['email', 'password', 'confirm_password']

    def create(self, validated_data):
        email = validated_data['email']
        password = validated_data['password']

        return UserService.register_user(email=email, password=password)
