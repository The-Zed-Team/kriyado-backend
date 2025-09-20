from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.crypto import get_random_string

from apps.account.models import *


class UserService:
    @staticmethod
    def register_user(email: str, password: str) -> User:

        user = User.objects.create_user(email=email, password=password, is_active=False)

        token = get_random_string(32)
        expires_at = timezone.now() + timedelta(minutes=10)
        UserActivationToken.objects.create(user=user, token=token, expires_at=expires_at)
        UserService.send_verification_email(user.email, token)
        return user

    @staticmethod
    def send_verification_email(email: str, token: str):
        activation_link = f"{settings.FRONTEND_URL}/activate/{token}/"
        send_mail(
            subject="Activate Your Account",
            message=f"Hi,\n\nActivate your account: {activation_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False
        )

    @staticmethod
    def activate_user(token: str) -> bool:
        try:
            activation = UserActivationToken.objects.get(token=token)
        except ObjectDoesNotExist:
            return False

        if activation.expires_at < timezone.now():
            return False

        user = activation.user
        user.is_active = True
        user.save()

        activation.delete(),
        return True
