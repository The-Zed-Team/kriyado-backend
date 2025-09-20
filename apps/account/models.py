import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from safedelete.models import SafeDeleteModel, SOFT_DELETE_CASCADE

from apps.account.managers import UserManager
from core.django.models.mixins import Timestamps


class User(AbstractBaseUser, PermissionsMixin, SafeDeleteModel, Timestamps):
    _safedelete_policy = SOFT_DELETE_CASCADE

    AUTH_PROVIDERS = (
        ("email", "Email"),
        ("phone", "Phone"),
        ("google", "Google"),
        ("apple", "Apple"),
        ("firebase", "Firebase"),
    )

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True, db_index=True
    )

    first_name = models.CharField("First Name", max_length=100, blank=False, null=False)
    middle_name = models.CharField("Middle Name", max_length=100, blank=True, null=True)
    last_name = models.CharField("Last Name", max_length=100, blank=True, null=True)

    user_type = models.CharField(
        "User Type",
        max_length=50,
        blank=False,
        null=False,
        choices=(
            ("customer", "Customer"),
            ("vendor", "Vendor"),
            ("admin", "Admin"),
            ("employee", "Employee"),
        ),
    )

    username = models.CharField(
        max_length=100, db_index=True, null=False, blank=False, unique=True
    )
    email = models.EmailField(
        "Email Address", max_length=255, db_index=True, unique=True, null=True
    )
    phone_number = models.CharField(
        "Phone Number", max_length=15, blank=True, null=True, db_index=True, unique=True
    )
    password = models.CharField("Password", max_length=128, null=True)
    email_verified = models.BooleanField("Email Verified", default=False)
    phone_verified = models.BooleanField("Phone Verified", default=False)

    auth_provider = models.CharField(
        "Auth Provider", max_length=50, blank=True, null=True, choices=AUTH_PROVIDERS
    )
    is_active = models.BooleanField("Active", default=True)
    activation_key = models.CharField(
        "Activation Key", max_length=100, blank=True, null=True, unique=True
    )  # used for activating user in case the user is created manually

    objects = UserManager()

    USERNAME_FIELD = "username"

    class Meta:
        app_label = "account"
        ordering = ["username"]


# This model stores data for a user's social media accounts.
# It links to the CustomUser model and stores provider-specific information.
class AuthenticationProviders(models.Model):
    PROVIDERS = (
        ("google", "Google"),
        ("apple", "Apple"),
        ("firebase", "Firebase"),
    )

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True, db_index=True
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="social_accounts"
    )
    provider = models.CharField(
        max_length=200,
        choices=PROVIDERS,
        help_text="The social account provider (e.g., 'google', 'apple').",
    )
    provider_uid = models.CharField(
        max_length=255,
        unique=True,
        help_text="The unique ID from the social account provider.",
    )
    extra_data = models.JSONField(
        blank=True,
        null=True,
        help_text="Additional data from the provider (e.g., tokens, profile data).",
    )

    def __str__(self):
        return f"{self.user.email}'s {self.provider} account"

    class Meta:
        unique_together = ("provider", "user")


# class UserActivationToken(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     user = models.OneToOneField(
#         User, on_delete=models.CASCADE, related_name="activation_token"
#     )
#     token = models.CharField(max_length=64, unique=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     expires_at = models.DateTimeField()

#     def __str__(self):
#         return f"{self.user.email} - {self.token}"
