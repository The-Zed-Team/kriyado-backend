from rest_framework.permissions import BasePermission

from apps.vendor.models import Vendor, VendorBranch, VendorBranchUser, VendorUser


class HasVendorPermission(BasePermission):
    """
    Check if the user has a specific vendor permission.
    """

    def has_permission(self, request, view):
        try:
            # basic vendor level permission
            vendor_id = request.headers.get("Vendor-ID")
            if not vendor_id:
                return False
            vendor = Vendor.objects.get(id=vendor_id)
            vendor_user = request.user.vendor_users.get(vendor_id=vendor_id)
            request.vendor = vendor
            request.vendor_user = vendor_user
            if vendor_user.is_super_admin:
                return True
            # TODO: handle specific permissions later
            # accept view.permissions dict and check for view specific permission before processing the request
            return True
        except Vendor.DoesNotExist:
            return False
        except VendorUser.DoesNotExist:
            return False

    def has_object_permission(self, request, view, obj):
        return True


class HasVendorBranchPermission(BasePermission):
    """
    Check if the user has a specific vendor branch permission.
    """

    def has_permission(self, request, view):
        try:
            # basic vendor level permission
            branch_id = request.headers.get("VendorBranch-ID")
            if not branch_id:
                return False
            vendor_branch = VendorBranch.objects.get(id=branch_id)
            request.vendor_branch = vendor_branch
            try:
                vendor_branch_user = request.user.vendor_branch_users.get(
                    vendor_branch_id=branch_id
                )
                if vendor_branch_user.is_super_admin:
                    return True
            except VendorBranchUser.DoesNotExist:
                vendor_user = request.user.vendor_users.get(
                    vendor_id=vendor_branch.vendor_id
                )
                if vendor_user.is_super_admin:
                    return True
            # TODO: handle specific permissions later
            # accept view.permissions dict and check for view specific permission before processing the request
            return True
        except VendorBranch.DoesNotExist:
            return False
        except VendorBranchUser.DoesNotExist:
            return False
        except VendorUser.DoesNotExist:
            return False
