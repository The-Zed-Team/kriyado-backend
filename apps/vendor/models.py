from django.core.validators import MinValueValidator
from django.db import models

from apps.account.models import User


# Enum-like classes for choices to ensure data consistency
class BusinessType(models.TextChoices):
    WHOLESALE = "Wholesale", "Wholesale"
    RETAIL = "Retail", "Retail"
    WHOLESALE_AND_RETAIL = "Wholesale & Retail", "Wholesale & Retail"
    SERVICE_BASED = "Service based", "Service based"


class DiscountValueType(models.TextChoices):
    FLAT = "Flat", "Flat"
    PERCENTAGE = "Percentage", "Percentage"


class DiscountType(models.TextChoices):
    TOTAL_BILL = "Total Bill", "Total Bill"
    CATEGORY_BASED = "Category Based", "Category Based"
    SPECIAL_OFFER = "Special Offer", "Special Offer"


class Vendor(models.Model):
    """
    Core Vendor model.
    Handles basic user-related details and links to Django's built-in User model.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=200, null=False, blank=False)
    contact_number = models.CharField(
        max_length=15, unique=True, help_text="Mobile number for sign-up and OTP."
    )
    is_registered = models.BooleanField(
        default=False,
        help_text="Indicates if the vendor has completed the full registration wizard.",
    )

    def __str__(self):
        return self.user.username


class VendorProfile(models.Model):
    """
    Stores details from the three-step registration wizard, linked to the Vendor model.
    """

    vendor = models.OneToOneField(Vendor, on_delete=models.CASCADE)

    # Wizard 1 - Location
    shop_type = models.CharField(max_length=100)
    business_type = models.CharField(max_length=20, choices=BusinessType.choices)
    # country = models.CharField(max_length=50)
    # state = models.CharField(max_length=50)
    # district = models.CharField(max_length=50)
    # shop_locality = models.CharField(max_length=100)
    # nearby_town = models.CharField(max_length=100)
    # pin_code = models.CharField(max_length=10)
    # organization_name = models.CharField(max_length=255)
    owner_name = models.CharField(max_length=100, blank=True, null=True)
    mobile_number = models.CharField(max_length=15)
    # key_person_name = models.CharField(max_length=100)
    # key_person_contact_number = models.CharField(max_length=15)

    # Wizard 2 - Contact
    land_phone = models.CharField(max_length=20, blank=True, null=True)
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
        return f"Profile for {self.vendor.user.username}"


class VendorBranch(models.Model):
    """
    Stores details for multiple vendor branches.
    """

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

    def __str__(self):
        return f"Branch for {self.vendor.user.username} in {self.shop_locality}"


class VendorDiscount(models.Model):
    """
    Stores different types of discounts offered by the vendor.
    """

    vendor = models.ForeignKey(
        Vendor, on_delete=models.CASCADE, related_name="discounts"
    )
    discount_type = models.CharField(max_length=20, choices=DiscountType.choices)
    value_type = models.CharField(max_length=10, choices=DiscountValueType.choices)
    value = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )

    # Fields specific to certain discount types
    category = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Category for category-based discounts.",
    )
    special_offer_text = models.TextField(
        blank=True, null=True, help_text="Text for special offers."
    )
    expiry_date = models.DateField(blank=True, null=True)

    # Links to the branches this discount applies to
    branches = models.ManyToManyField(
        VendorBranch, related_name="discounts", blank=True
    )

    def __str__(self):
        return f"{self.discount_type} Discount for {self.vendor.user.username}"


class VendorPendingUpdate(models.Model):
    """
    Stores pending changes made by the vendor that require admin verification.
    The 'changes' field will store a JSON representation of the updated data.
    """

    vendor = models.OneToOneField(Vendor, on_delete=models.CASCADE)
    changes = models.JSONField(help_text="JSON representation of the pending updates.")
    updated_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"Pending update for {self.vendor.user.username}"
