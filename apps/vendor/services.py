from apps.vendor.models import *


def create_vendor_profile(validated_data):
    user = validated_data.pop('user')
    branch_details = {
        'country': validated_data.get('country'),
        'state': validated_data.get('state'),
        'district': validated_data.get('district'),
        'shop_locality': validated_data.get('shop_locality'),
        'nearby_town': validated_data.get('nearby_town'),
        'pin_code': validated_data.get('pin_code'),
        'key_person_name': validated_data.get('key_person_name'),
        'key_person_contact_number': validated_data.get('key_person_contact_number'),
        'land_phone': validated_data.get('land_phone'),
    }

    vendor_instance = Vendor.objects.create(user=user)
    vendor_profile_instance = VendorProfile.objects.create(vendor=vendor_instance, **validated_data)
    VendorBranch.objects.create(
        vendor=vendor_instance,
        **branch_details
    )
    vendor_instance.is_registered = True
    vendor_instance.save()

    return vendor_profile_instance
