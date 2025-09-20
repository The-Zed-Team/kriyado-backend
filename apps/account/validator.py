from rest_framework import serializers


class ConfirmPasswordValidator:
    requires_context = True  # allows access to serializer instance

    def __call__(self, confirm_password, serializer):
        password = serializer.initial_data.get('password')
        if password != confirm_password:
            raise serializers.ValidationError("Passwords do not match.")
