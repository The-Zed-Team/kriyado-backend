import uuid

from django.db import models
from safedelete.models import SOFT_DELETE_CASCADE, SafeDeleteModel

from apps.account.models import User
from core.django.models.mixins import Timestamps

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
    "default_branch": {
        "default_branch": {"required": True},
    },
    # Step 2 - Contact details
    "contact_details": {
        "land_phone": {"required": True},
        "registered_address": {"required": True},
        "website": {"required": True},
        "facebook_link": {"required": True},
        "instagram_link": {"required": True},
        "google_map_link": {"required": True},
        "youtube_link": {"required": True},
    },
    # Step 3 - Store details
    "store_details": {
        "working_hours_from": {"required": True},
        "working_hours_to": {"required": True},
        "home_delivery": {"required": True},
        "logo": {"required": False},
        "store_photo": {"required": False},
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

    BUSINESS_TYPE_CHOICES = (
        ("Wholesale", "Wholesale"),
        ("Retail", "Retail"),
        ("Wholesale & Retail", "Wholesale & Retail"),
        ("Service based", "Service based"),
    )

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True, db_index=True
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="vendor")
    name = models.CharField(max_length=200, null=False, blank=False)
    contact_number = models.CharField(
        max_length=15, unique=True, help_text="Mobile number for sign-up and OTP."
    )
    shop_type = models.ForeignKey(
        ShopType, on_delete=models.RESTRICT, null=False, blank=False
    )
    business_type = models.CharField(
        max_length=20, choices=BUSINESS_TYPE_CHOICES, null=False, blank=False
    )
    owner_name = models.CharField(max_length=100, blank=True, null=True)
    is_onboarded = models.BooleanField(default=False)

    def update_vendor_onboarding_status(self) -> tuple[bool, dict]:
        """
        Evaluates and updates the vendor's onboarding status based on the completion of required steps.
        Returns a tuple containing the overall onboarding status and a dictionary with the completion status of each step.
        """
        step_status = {}
        if self.is_onboarded:
            return True, {key: True for key in VENDOR_ONBOARDING_STEPS.keys()}
        if not hasattr(self, "profile"):
            return False, {key: False for key in VENDOR_ONBOARDING_STEPS.keys()}

        profile = self.profile

        for key, data in VENDOR_ONBOARDING_STEPS.items():
            if not profile or self.is_onboarded:
                step_status[key] = self.is_onboarded
                continue

            step_completed = True
            for field, rules in data.items():
                if rules.get("required", False):
                    if not getattr(profile, field, None):
                        step_completed = False
                        break
            step_status[key] = step_completed

        if not self.is_onboarded:
            self.is_onboarded = all(step_status.values())
            self.save(update_fields=["is_onboarded"])

        return self.is_onboarded, step_status

    def __str__(self):
        return self.user.username


class VendorProfile(SafeDeleteModel, Timestamps):
    """
    Stores details from the three-step registration wizard, linked to the Vendor model.
    """

    _safedelete_policy = SOFT_DELETE_CASCADE

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True, db_index=True
    )
    vendor = models.OneToOneField(
        Vendor, on_delete=models.CASCADE, related_name="profile"
    )

    default_branch = models.ForeignKey(
        "VendorBranch", on_delete=models.RESTRICT, null=True, blank=True
    )

    # Wizard 2 - Contact
    registered_address = models.TextField(blank=True, null=True)

    website = models.URLField(max_length=255, blank=True, null=True)
    facebook_link = models.URLField(max_length=255, blank=True, null=True)
    instagram_link = models.URLField(max_length=255, blank=True, null=True)
    google_map_link = models.URLField(max_length=255, blank=True, null=True)
    youtube_link = models.URLField(max_length=255, blank=True, null=True)

    # Wizard 3 - Store Details
    working_hours_from = models.TimeField(blank=True, null=True)
    working_hours_to = models.TimeField(blank=True, null=True)
    home_delivery = models.BooleanField(default=False)

    logo = models.ImageField(upload_to="vendor_logos/", blank=True, null=True)
    store_photo = models.ImageField(
        upload_to="vendor_store_photos/", blank=True, null=True
    )

    def __str__(self):
        return f"Profile for {self.vendor.name}"


class VendorBranch(SafeDeleteModel, Timestamps):
    """
    Stores details for multiple vendor branches.
    """

    _safedelete_policy = SOFT_DELETE_CASCADE

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True, db_index=True
    )
    vendor = models.ForeignKey(
        Vendor, on_delete=models.CASCADE, related_name="branches"
    )
    country = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
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
    def __str__(self):
        return f"Branch for {self.vendor.user.username} in {self.shop_locality}"


class Discount(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('total_bill', 'Total Bill'),
        ('category', 'Category Based'),
        ('special', 'Special Offer'),
    ]

    VALUE_TYPE_CHOICES = [
        ('flat', 'Flat'),
        ('percent', 'Percentage'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending Verification'),
        ('active', 'Active'),
    ]

    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='discounts')
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)
    category = models.CharField(max_length=100, blank=True, null=True)

    value_type = models.CharField(max_length=10, choices=VALUE_TYPE_CHOICES)
    value = models.DecimalField(max_digits=10, decimal_places=2)

    description = models.TextField(blank=True, null=True)
    vendorBranch = models.ManyToManyField(VendorBranch, related_name='discounts')
    min_purchase = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.discount_type} - {self.value}{'%' if self.value_type == 'percent' else ''}"
