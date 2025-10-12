from rest_framework import authentication, exceptions
from django.contrib.auth.models import User

from apps.account.models import AuthenticationProviders
from . import firebase_client


class FirebaseAuthentication(authentication.BaseAuthentication):
    """
    Authenticate using Firebase ID token passed in the Authorization header as Bearer token.
    """

    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None  # No header means DRF will try other auth classes

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise exceptions.AuthenticationFailed("Invalid Authorization header")

        id_token = parts[1]

        try:
            decoded_token = firebase_client.verify_token(id_token)
        except Exception as e:
            raise exceptions.AuthenticationFailed(
                f"Invalid Firebase ID token: {str(e)}"
            )

        if not decoded_token.valid:
            raise exceptions.AuthenticationFailed("Invalid Firebase ID token")

        uid = decoded_token.decoded_token.uid

        if not uid:
            raise exceptions.AuthenticationFailed("Invalid token: no UID found")
        try:
            auth_provider = AuthenticationProviders.objects.select_related("user").get(
                provider="firebase", provider_uid=uid
            )
        except AuthenticationProviders.DoesNotExist:
            raise exceptions.AuthenticationFailed("No user associated with this token")
        except AuthenticationProviders.MultipleObjectsReturned:
            raise exceptions.AuthenticationFailed("Multiple users found for this token")

        return (auth_provider.user, None)
