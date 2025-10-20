import uuid

from django.db import models
from safedelete.models import SafeDeleteModel

from apps.vendor.models import VendorBranch
from core.django.models.mixins import Timestamps

DISCOUNT_TYPE_CHOICES = [
    ("flat", "Flat"),
    ("percent", "Percent"),
    ("category_based", "Category Based"),
]


class Category(SafeDeleteModel, Timestamps):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, null=False, unique=True)
    description = models.CharField(max_length=255)
    created_by = models.ForeignKey(
        "account.User", on_delete=models.SET_NULL, null=True, blank=True
    )


class DiscountPreset(SafeDeleteModel, Timestamps):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=50, choices=DISCOUNT_TYPE_CHOICES)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    purchase_above = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_by = models.ForeignKey(
        "account.User", on_delete=models.SET_NULL, null=True, blank=True
    )


class VendorBranchDiscount(SafeDeleteModel, Timestamps):
    DISCOUNT_APPROVAL_STATUS = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]
    DISCOUNT_STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("expired", "Expired"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=50, choices=DISCOUNT_TYPE_CHOICES, blank=True, null=True)
    vendor_branch = models.ForeignKey(
        VendorBranch, on_delete=models.CASCADE, related_name="vendor_discounts"
    )
    name = models.CharField(max_length=100, blank=True, null=True)

    description = models.CharField(max_length=255, blank=True, null=True)
    preset = models.ForeignKey(
        DiscountPreset,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="vendor_discounts",
    )
    purchase_above = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True
    )
    vendor_branch = models.ForeignKey(
        VendorBranch, on_delete=models.CASCADE, related_name="discounts"
    )
    approval_status = models.CharField(
        max_length=50, choices=DISCOUNT_APPROVAL_STATUS, default="pending"
    )
    approved_by = models.ForeignKey(
        "account.User", on_delete=models.SET_NULL, null=True, blank=True
    )
    status = models.CharField(
        max_length=10, choices=DISCOUNT_STATUS_CHOICES, default="inactive"
    )

    class Meta:
        verbose_name = "Vendor Discount"
        verbose_name_plural = "Vendor Discounts"

    def __str__(self):
        return f"{self.vendor_branch.name} - {self.preset.name}"


# class TotalBillPreset(SafeDeleteModel, Timestamps):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     name = models.CharField(max_length=100)
#     code = models.CharField(max_length=50, unique=True)
#     description = models.CharField(max_length=255)
#     is_active = models.BooleanField(default=True)

#     class Meta:
#         verbose_name = "Discount"
#         verbose_name_plural = "Discounts"
#         ordering = ["id"]

#     def __str__(self):
#         return self.name


# # Discount Model
# class Discount(models.Model):
#     VALUE_TYPE_CHOICES = [
#         ("flat", "Flat"),
#         ("percent", "%"),
#     ]

#     APPROVAL_STATUS = [
#         ("pending", "Pending"),
#         ("approved", "Approved"),
#         ("rejected", "Rejected"),
#     ]

#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     name = models.CharField(max_length=255)
#     value_type = models.CharField(max_length=10, choices=VALUE_TYPE_CHOICES)
#     value = models.DecimalField(max_digits=10, decimal_places=2)
#     min_purchase_amount = models.DecimalField(
#         max_digits=10, decimal_places=2, blank=True, null=True
#     )
#     branches = models.ManyToManyField(VendorBranch, related_name="discounts")
#     preset = models.ForeignKey(
#         TotalBillPreset, on_delete=models.SET_NULL, blank=True, null=True
#     )

#     approval_status = models.CharField(
#         max_length=10, choices=APPROVAL_STATUS, default="pending"
#     )
#     approved_by = models.ForeignKey(
#         User,
#         on_delete=models.SET_NULL,
#         blank=True,
#         null=True,
#         related_name="approved_discounts",
#     )
#     approved_at = models.DateTimeField(blank=True, null=True)

#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"{self.name} ({self.value_type} {self.value})"
