import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager
from safedelete.models import SafeDeleteModel, SOFT_DELETE_CASCADE
from safedelete.managers import SafeDeleteManager

from core.django.models.mixins import Timestamps


class UserManager(BaseUserManager, SafeDeleteManager):
    def get_by_natural_key_and_store(self, username, store, user_type):
        user_type = user_type if user_type else "su"
        return self.get(
            **{
                self.model.USERNAME_FIELD: username,
                "deleted__isnull": True,
                "store": store,
                "user_type": user_type,
                "is_guest": False,
            }
        )

    def create_user(self, email, password=None, **kwargs):
        email = self.normalize_email(email)
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, **kwargs):
        user = self.create_user(**kwargs)
        user.is_superuser = True
        user.is_staff = True
        user.user_type = "su"
        user.save(using=self._db)
        return user


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
    username = models.CharField(
        max_length=100, db_index=True, null=False, blank=False, unique=True
    )
    email = models.EmailField(
        ("Email Address"), max_length=255, db_index=True, unique=True, null=True
    )
    phone = models.CharField(
        ("Phone Number"),
        max_length=15,
        blank=True,
        null=True,
        db_index=True,
        unique=True,
    )
    password = models.CharField("Password", max_length=128, null=True)

    auth_provider = models.CharField(
        max_length=50, blank=True, null=True, choices=AUTH_PROVIDERS
    )  # specify which auth provider to use
    is_active = models.BooleanField("Active", default=True)
    activation_key = models.CharField(
        max_length=100, blank=True, null=True, unique=True
    )  # used for activating user in case the user is created manually

    objects = UserManager()

    USERNAME_FIELD = "username"

    class Meta:
        app_label = "account"
        ordering = ["username"]


# This model stores data for a user's social media accounts.
# It links to the CustomUser model and stores provider-specific information.
class SocialAccount(models.Model):
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
