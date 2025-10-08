# apps/vendor/admin.py

from django.contrib import admin

from .models import Vendor, VendorProfile, VendorBranch, ShopType


@admin.register(ShopType)
class ShopTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "description", "created_at", "updated_at")
    search_fields = ("name", "code")
    ordering = ("name",)
    readonly_fields = ("id", "created_at", "updated_at")


class VendorProfileInline(admin.StackedInline):
    model = VendorProfile
    extra = 0
    readonly_fields = ("id", "vendor")
    fields = (
        "default_branch",
        "registered_address",
        "website",
        "facebook_link",
        "instagram_link",
        "google_map_link",
        "youtube_link",
        "working_hours_from",
        "working_hours_to",
        "home_delivery",
        "logo",
        "store_photo",
    )


class VendorBranchInline(admin.TabularInline):
    model = VendorBranch
    extra = 1
    readonly_fields = ("id",)
    fields = (
        "country",
        "state",
        "district",
        "shop_locality",
        "nearby_town",
        "pin_code",
        "key_person_name",
        "key_person_contact_number",
        "land_phone",
        "latitude",
        "longitude",
    )


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "name",
        "contact_number",
        "shop_type",
        "business_type",
        "owner_name",
        "is_onboarded",
        "created_at",
        "updated_at",
    )
    search_fields = ("name", "user__username", "contact_number")
    list_filter = ("shop_type", "business_type", "is_onboarded")
    ordering = ("name",)
    readonly_fields = ("id", "is_onboarded", "created_at", "updated_at")
    inlines = [VendorProfileInline, VendorBranchInline]
