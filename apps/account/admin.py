# apps/account/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, AuthenticationProviders


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Fields to display in the user list
    list_display = (
        "username",
        "email",
        "phone_number",
        "is_active",
        "email_verified",
        "phone_verified",
        "auth_provider",
        "created_at",
        "updated_at",
    )
    # Fields that can be searched
    search_fields = ("username", "email", "phone_number")
    # Filters shown on the right side of admin list page
    list_filter = ("is_active", "email_verified", "auth_provider")

    ordering = ("username",)
    readonly_fields = ("id", "created_at", "updated_at")

    fieldsets = (
        ("Basic Info", {"fields": ("username", "email", "phone_number", "password")}),
        (
            "Verification",
            {"fields": ("email_verified", "phone_verified", "auth_provider")},
        ),
        ("Status", {"fields": ("is_active",)}),
        ("Meta", {"fields": ("id", "created_at", "updated_at")}),
        ("Permissions", {"fields": ("is_superuser", "groups", "user_permissions")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "phone_number",
                    "password1",
                    "password2",
                    "is_active",
                ),
            },
        ),
    )


@admin.register(AuthenticationProviders)
class AuthenticationProvidersAdmin(admin.ModelAdmin):
    list_display = ("user", "provider", "provider_uid")
    search_fields = ("user__username", "provider", "provider_uid")
    list_filter = ("provider",)
