from rest_framework import serializers

from core.authentication.firebase import firebase_client


class FirebaseUserAuthenticationRequestSerializer(serializers.Serializer):
    id_token = serializers.CharField(required=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    middle_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(required=False, allow_blank=True)
