from django.db import transaction
from rest_framework import serializers

from apps.vendor.models import *


class CreateVendorSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    def validate(self, attrs):
        if Vendor.objects.filter(created_by=self.context["user"]).exists():
            raise serializers.ValidationError(
                "Vendor profile already exists for this user."
            )
        return super().validate(attrs)

    @transaction.atomic
    def create(self, validated_data):
        user = self.context["user"]
        validated_data["created_by"] = user
        validated_data["code"] = f"KRY-{user.id.hex[:10].upper()}"

        vendor = super().create(validated_data)
        role = VendorUserRole.objects.create(
            name="Super Admin",
            vendor=vendor,
            description="Default role with all permissions.",
        )
        VendorUser.objects.create(
            user=user, vendor=vendor, role=role, is_super_admin=True
        )
        return vendor

    class Meta:
        model = Vendor
        fields = (
            "id",
            "name",
            "contact_number",
            "owner_name",
            "logo",
            "website",
            "default_branch_id",
        )
        read_only_fields = ("id", "default_branch_id")


class UpdateVendorSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    def validate(self, attrs):
        vendor = getattr(self.instance, "user", None)
        if vendor and vendor != self.context["user"]:
            raise serializers.ValidationError(
                "You cannot update another user's vendor profile."
            )
        return super().validate(attrs)

    class Meta:
        model = Vendor
        fields = (
            "id",
            "name",
            "contact_number",
            "owner_name",
            "logo",
            "website",
            "default_branch_id",
        )
        read_only_fields = ("id", "default_branch_id")


class ShopTypeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = ShopType
        fields = ("id", "name", "code", "description")


class VendorDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = (
            "id",
            "name",
            "contact_number",
            "owner_name",
            "is_onboarded",
            "branches",
            "default_branch",
        )
        depth = 2  # expands profile, default_branch inside profile, branches, shop_type


class VendorBranchSerializer(serializers.ModelSerializer):

    @transaction.atomic
    def create(self, validated_data):
        vendor = self.context["request"].vendor
        validated_data["vendor"] = vendor
        validated_data["code"] = (
            f"{vendor.code}-BR-{VendorBranch.objects.filter(vendor=vendor).count() + 1}"
        )
        branch = super().create(validated_data)
        if not vendor.default_branch_id:
            vendor.default_branch = branch
            vendor.save()

        if not VendorBranchProfile.objects.filter(vendor_branch=branch).exists():
            branch.profile = VendorBranchProfile.objects.create(vendor_branch=branch)

        VendorBranchUser.objects.create(
            user=self.context["request"].user,
            vendor_branch=branch,
            is_super_admin=True,
            role=VendorBranchUserRole.objects.create(
                name="Super Admin",
                vendor_branch=branch,
                description="Default role with all permissions.",
            ),
        )

        return branch

    class Meta:
        model = VendorBranch
        fields = [
            "id",
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
            "shop_type",
            "business_type",
        ]
        read_only_fields = [
            "id",
            "datetime_created",
            "datetime_updated",
        ]


class VendorBranchMiniSerializer(serializers.ModelSerializer):
    """Used for nested read representation of default_branch"""

    country = serializers.CharField(source="country.name", read_only=True)
    state = serializers.CharField(source="state.name", read_only=True)
    district = serializers.CharField(source="district.name", read_only=True)

    class Meta:
        model = VendorBranch
        fields = ["id", "country", "state", "district"]  # include only essential fields


class VendorBranchProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = VendorBranchProfile
        fields = [
            "id",
            "land_phone",
            "datetime_created",
            "datetime_updated",
            "registered_address",
            "facebook_link",
            "instagram_link",
            "google_map_link",
            "youtube_link",
            "store_photo",
            "vendor_branch",
            "working_hours_from",
            "working_hours_to",
            "has_home_delivery",
        ]
        read_only_fields = [
            "id",
            "datetime_created",
            "datetime_updated",
            "vendor_branch",
        ]
        extra_kwargs = {
            "registered_address": {
                "required": True,
                "error_messages": {
                    "required": "Registered address is required.",
                    "blank": "Registered address cannot be blank.",
                },
            },
            "google_map_link": {
                "required": True,
                "error_messages": {
                    "required": "Google Map link is required.",
                    "blank": "Google Map link cannot be blank.",
                    "invalid": "Please enter a valid Google Map URL.",
                },
            },
            "has_home_delivery": {
                "required": True,
                "error_messages": {
                    "required": "Please specify if home delivery is available.",
                    "null": "This field cannot be null.",
                },
            },
        }

class VendorUserInviteSerializer(serializers.ModelSerializer):

    def validate(self, attrs):
        validated_data = super().validate(attrs)
        vendor = validated_data.get("vendor")
        vendor_branch = validated_data.get("vendor_branch")
        if not vendor and not vendor_branch:
            raise serializers.ValidationError(
                "You must invite the user to either a vendor or a vendor branch."
            )
        if vendor and vendor_branch:
            raise serializers.ValidationError(
                "You can only invite the user to either a vendor or a vendor branch, not both."
            )
        if (vendor and vendor != self.context["request"].vendor) or (
            vendor_branch and vendor_branch.vendor != self.context["request"].vendor
        ):
            raise serializers.ValidationError(
                "You can only invite users to your vendor or branches of your vendor."
            )
        if VendorUserInvites.objects.filter(
            email=validated_data["email"],
            vendor=vendor,
            vendor_branch=vendor_branch,
            status="pending",
        ).exists():
            raise serializers.ValidationError(
                "An invite has already been sent to this email for the specified vendor or branch."
            )
        return validated_data

    @transaction.atomic
    def create(self, validated_data):
        validated_data["invited_by"] = self.context["request"].user
        user = User.objects.filter(email=validated_data["email"]).first()
        vendor = validated_data.get("vendor")
        vendor_branch = validated_data.get("vendor_branch")

        if user:
            validated_data["user"] = user

            if vendor:
                if VendorUser.objects.filter(user=user, vendor=vendor).exists():
                    raise serializers.ValidationError(
                        {
                            "non_field_errors": [
                                "This user is already a member of the vendor."
                            ]
                        }
                    )
                VendorUser.objects.create(
                    user=user,
                    vendor=vendor,
                    is_super_admin=False,
                )
                validated_data["status"] = "accepted"

            if vendor_branch:
                if VendorBranchUser.objects.filter(
                    user=user, vendor_branch=vendor_branch
                ).exists():
                    raise serializers.ValidationError(
                        {
                            "non_field_errors": [
                                "This user is already a member of the vendor branch."
                            ]
                        }
                    )
                VendorBranchUser.objects.create(
                    user=user,
                    vendor_branch=vendor_branch,
                    is_super_admin=False,
                )
                validated_data["status"] = "accepted"
        return super().create(validated_data)

    class Meta:
        model = VendorUserInvites
        fields = [
            "id",
            "email",
            "vendor",
            "vendor_branch",
            "status",
            "token",
            "invited_by",
        ]
        read_only_fields = ["id", "status", "token", "invited_by"]
