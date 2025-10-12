import re
import unicodedata
import uuid

from django.db import models
from django.db.models import Q
from safedelete.models import SOFT_DELETE_CASCADE, SafeDeleteModel

from apps.account.models import User
from apps.shared.models import Country, District, State
from core.django.models.mixins import Timestamps
from core.django.models.utils import get_nested_attr

# DISCOUNT_VALUE_TYPE_CHOICES = (
#     ("Flat", "Flat"),
#     ("Percentage", "Percentage"),
# )

# DISCOUNT_TYPE_CHOICES = (
#     ("Total Bill", "Total Bill"),
#     ("Category Based", "Category Based"),
#     ("Special Offer", "Special Offer"),
# )

VENDOR_ONBOARDING_STEPS = {
    # Step 1 - default branch
    "create_vendor": {
        "id": {"required": True},
    },
    "default_branch": {
        "default_branch__country": {"required": True},
        "default_branch__state": {"required": True},
        "default_branch__district": {"required": True},
        "default_branch__shop_type": {"required": True},
        "default_branch__business_type": {"required": True},
    },
    # Step 2 - Contact details
    "branch_profile": {
        "default_branch__profile__land_phone": {"required": True},
        "default_branch__profile__registered_address": {"required": True},
        "default_branch__profile__facebook_link": {"required": False},
        "default_branch__profile__instagram_link": {"required": False},
        "default_branch__profile__google_map_link": {"required": True},
        "default_branch__profile__youtube_link": {"required": False},
        "default_branch__profile__working_hours_from": {"required": True},
        "default_branch__profile__working_hours_to": {"required": True},
        "default_branch__profile__has_home_delivery": {"required": True},
        "default_branch__profile__store_photo": {"required": False},
    },
}


class ShopType(Timestamps):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True, db_index=True
    )
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)


class Vendor(SafeDeleteModel, Timestamps):
    """
    Core Vendor model.
    Handles basic user-related details and links to Django's built-in User model.
    """

    _safedelete_policy = SOFT_DELETE_CASCADE

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True, db_index=True
    )
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200, null=False, blank=False)
    contact_number = models.CharField(
        max_length=15, unique=True, help_text="Mobile number for sign-up and OTP."
    )
    owner_name = models.CharField(max_length=100, blank=True, null=True)
    logo = models.ImageField(upload_to="vendor_logos/", blank=True, null=True)
    website = models.URLField(max_length=255, blank=True, null=True)

    default_branch = models.ForeignKey(
        "VendorBranch",
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
        related_name="default_for_vendor",
    )
    created_by = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="vendor"
    )
    is_onboarded = models.BooleanField(default=False)

    def update_vendor_onboarding_status(self) -> tuple[bool, dict]:
        """
        Evaluates and updates the vendor's onboarding status based on the completion of required steps.
        Returns a tuple containing the overall onboarding status and a dictionary with the completion status of each step.
        """
        step_status = {}
        if self.is_onboarded:
            return True, {key: True for key in VENDOR_ONBOARDING_STEPS.keys()}

        for key, data in VENDOR_ONBOARDING_STEPS.items():
            step_completed = True
            for field, rules in data.items():
                if rules.get("required", False):
                    if not get_nested_attr(self, field):
                        step_completed = False
                        break
            step_status[key] = step_completed

        if not self.is_onboarded:
            self.is_onboarded = all(step_status.values())
            self.save(update_fields=["is_onboarded"])

        return self.is_onboarded, step_status

    def __str__(self):
        return self.name


class VendorBranch(SafeDeleteModel, Timestamps):
    """
    Stores details for multiple vendor branches.
    """

    BUSINESS_TYPE_CHOICES = (
        ("Wholesale", "Wholesale"),
        ("Retail", "Retail"),
        ("Wholesale & Retail", "Wholesale & Retail"),
        ("Service based", "Service based"),
    )

    _safedelete_policy = SOFT_DELETE_CASCADE

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True, db_index=True
    )
    code = models.CharField(max_length=20, null=False, blank=False)
    vendor = models.ForeignKey(
        Vendor, on_delete=models.CASCADE, related_name="branches"
    )
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, null=False, blank=False
    )
    state = models.ForeignKey(State, on_delete=models.CASCADE, null=False, blank=False)
    district = models.ForeignKey(
        District, on_delete=models.CASCADE, null=False, blank=False
    )
    shop_type = models.ForeignKey(
        ShopType, on_delete=models.RESTRICT, null=False, blank=False
    )
    business_type = models.CharField(
        max_length=20, choices=BUSINESS_TYPE_CHOICES, null=False, blank=False
    )
    shop_locality = models.CharField(max_length=100)
    nearby_town = models.CharField(max_length=100)
    pin_code = models.CharField(max_length=10)
    key_person_name = models.CharField(max_length=100)
    key_person_contact_number = models.CharField(max_length=15)
    land_phone = models.CharField(max_length=20, blank=True, null=True)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True
    )

    class Meta:
        unique_together = ("vendor", "code")

    def __str__(self):
        return f"Branch for {self.vendor.user.username} in {self.shop_locality}"


class VendorBranchProfile(SafeDeleteModel, Timestamps):
    """
    Stores details from the three-step registration wizard, linked to the Vendor model.
    """

    _safedelete_policy = SOFT_DELETE_CASCADE

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True, db_index=True
    )
    vendor_branch = models.OneToOneField(
        VendorBranch, on_delete=models.CASCADE, related_name="profile"
    )
    # Wizard 2 - Contact
    registered_address = models.TextField(blank=True, null=True)
    land_phone = models.CharField(max_length=20, blank=True, null=True)

    facebook_link = models.URLField(max_length=255, blank=True, null=True)
    instagram_link = models.URLField(max_length=255, blank=True, null=True)
    google_map_link = models.URLField(max_length=255, blank=True, null=True)
    youtube_link = models.URLField(max_length=255, blank=True, null=True)
    store_photo = models.ImageField(
        upload_to="vendor_store_photos/", blank=True, null=True
    )

    # Wizard 3 - Store Details
    working_hours_from = models.TimeField(blank=True, null=True)
    working_hours_to = models.TimeField(blank=True, null=True)
    has_home_delivery = models.BooleanField(default=False)

    def __str__(self):
        return f"Profile for {self.vendor_branch.code}"


class VendorUserRole(SafeDeleteModel, Timestamps):
    """
    Defines roles for vendor users, allowing role-based access control.
    """

    _safedelete_policy = SOFT_DELETE_CASCADE

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True, db_index=True
    )
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    vendor = models.ForeignKey(
        Vendor, on_delete=models.RESTRICT, null=False, blank=False
    )
    acl = models.JSONField(default=dict, help_text="JSON field to store ACL data.")

    def save(self, keep_deleted=False, **kwargs):
        name_normalized = unicodedata.normalize("NFKD", self.name)
        code = (
            re.sub(r"[^\w]+", "_", name_normalized, flags=re.UNICODE)
            .strip("_")
            .lower()
            .replace("__", "_")
        )
        self.code = code
        return super().save(keep_deleted, **kwargs)

    class Meta:
        unique_together = ("vendor", "code")

    def __str__(self):
        return self.name


class VendorUser(SafeDeleteModel, Timestamps):
    """
    Links users to vendors, allowing multiple users to be associated with a single vendor.
    """

    _safedelete_policy = SOFT_DELETE_CASCADE

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True, db_index=True
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="vendor_users"
    )
    vendor = models.ForeignKey(
        Vendor, on_delete=models.CASCADE, related_name="vendor_users"
    )
    role = models.ForeignKey(
        VendorUserRole, on_delete=models.SET_NULL, null=True, blank=True
    )
    acl = models.JSONField(default=dict, help_text="JSON field to store ACL data.")
    is_super_admin = models.BooleanField(default=False)

    class Meta:
        unique_together = ("user", "vendor")

    @classmethod
    def check_has_permission(
        cls,
        user: User,
        vendor: Vendor,
        permission: str | None = None,
        raise_exception: bool = True,
    ) -> bool:
        try:
            vendor_user = cls.objects.get(user=user, vendor=vendor)
            if vendor_user.is_super_admin:
                return True
            return True
        except cls.DoesNotExist:
            if raise_exception:
                raise PermissionError("User does not have the required permission.")
            return False

    def __str__(self):
        return f"{self.user.username} - {self.vendor.name}"


class VendorBranchUserRole(SafeDeleteModel, Timestamps):
    """
    Defines roles for vendor branch users, allowing role-based access control at branch level.
    """

    _safedelete_policy = SOFT_DELETE_CASCADE

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True, db_index=True
    )
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)
    vendor_branch = models.ForeignKey(
        VendorBranch,
        on_delete=models.RESTRICT,
        null=False,
        blank=False,
        related_name="roles",
    )
    acl = models.JSONField(default=dict, help_text="JSON field to store ACL data.")

    def save(self, keep_deleted=False, **kwargs):
        name_normalized = unicodedata.normalize("NFKD", self.name)
        code = (
            re.sub(r"[^\w]+", "_", name_normalized, flags=re.UNICODE)
            .strip("_")
            .lower()
            .replace("__", "_")
        )
        self.code = code
        return super().save(keep_deleted, **kwargs)

    class Meta:
        unique_together = ("vendor_branch", "code")

    def __str__(self):
        return self.name


class VendorBranchUser(SafeDeleteModel, Timestamps):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True, db_index=True
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="vendor_branch_users"
    )
    vendor_branch = models.ForeignKey(
        "vendor.VendorBranch", on_delete=models.CASCADE, related_name="branch_users"
    )
    is_super_admin = models.BooleanField(default=False)
    role = models.ForeignKey(
        VendorBranchUserRole, on_delete=models.SET_NULL, null=True, blank=True
    )
    acl = models.JSONField(default=dict, help_text="JSON field to store ACL data.")

    def clean_acl(self):
        """
        Validates and cleans the ACL data before saving.
        """

    class Meta:
        unique_together = ("user", "vendor_branch")

    def __str__(self):
        return f"{self.user.username} - {self.vendor_branch.shop_locality}"

    @classmethod
    def check_has_permission(
        cls,
        user: User,
        vendor_branch: VendorBranch,
        permission: str | None = None,
        raise_exception: bool = True,
    ) -> bool:
        try:
            branch_user = cls.objects.get(user=user, vendor_branch=vendor_branch)
            if branch_user.is_super_admin:
                return True
            return True
        except cls.DoesNotExist:
            if raise_exception:
                raise PermissionError("User does not have the required permission.")
            return False


class VendorUserInvites(SafeDeleteModel, Timestamps):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True, db_index=True
    )
    email = models.EmailField(max_length=255)
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE,
        related_name="user_invites",
        null=True,
        blank=False,
    )
    vendor_branch = models.ForeignKey(
        VendorBranch,
        on_delete=models.CASCADE,
        related_name="branch_user_invites",
        null=True,
        blank=False,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="vendor_user_invites",
        null=True,
        blank=True,
    )
    invited_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="sent_vendor_invites", null=True
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("accepted", "Accepted"),
            ("declined", "Declined"),
        ],
        default="pending",
    )
    token = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)

    def accept_invite(self, user: User):
        if self.status != "pending":
            raise ValueError("Invite has already been responded to.")
        self.user = user
        if self.vendor:
            if VendorUser.objects.filter(user=user, vendor=self.vendor).exists():
                self.status = "declined"
            else:
                VendorUser.objects.create(user=user, vendor=self.vendor)
                self.status = "accepted"
        elif self.vendor_branch:
            if VendorBranchUser.objects.filter(
                user=user, vendor_branch=self.vendor_branch
            ).exists():
                self.status = "declined"
            else:
                VendorBranchUser.objects.create(
                    user=user, vendor_branch=self.vendor_branch
                )
                self.status = "accepted"
        self.save(update_fields=["user", "status"])

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(
                    # Exactly one of them should be NOT NULL
                    (Q(vendor__isnull=False) & Q(vendor_branch__isnull=True))
                    | (Q(vendor__isnull=True) & Q(vendor_branch__isnull=False))
                ),
                name="vendor_or_vendor_branch_only",
            )
        ]
        unique_together = ("email", "vendor", "vendor_branch", "status")
