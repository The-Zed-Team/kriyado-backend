from django.contrib.auth.password_validation import validate_password

from services import *
from validator import *


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
