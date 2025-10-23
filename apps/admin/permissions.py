# from rest_framework.permissions import BasePermission
#
# from apps.admin.models import Admin, AdminUser
#
#
# class HasAdminPermission(BasePermission):
#     """
#     Check if the user has a specific admin permission.
#     """
#
#     def has_permission(self, request, view):
#         try:
#             # basic admin level permission
#             admin_id = request.headers.get("Admin-ID")
#             if not admin_id:
#                 return False
#             admin = Admin.objects.get(id=admin_id)
#             print(request.user)
#             admin_user = request.user.admin_users.get(admin_id=admin_id)
#             request.admin = admin
#             request.admin_user = admin_user
#             print(admin, admin_user)
#             if admin_user.is_super_admin:
#                 return True
#             # TODO: handle specific permissions later
#             # accept view.permissions dict and check for view specific permission before processing the request
#             return True
#         except Admin.DoesNotExist:
#             return False
#         except AdminUser.DoesNotExist:
#             return False
#
#     def has_object_permission(self, request, view, obj):
#         return True


import logging
from rest_framework.permissions import BasePermission
from apps.admin.models import Admin, AdminUser

logger = logging.getLogger(__name__)
class HasAdminPermission(BasePermission):
    def has_permission(self, request, view):
        admin_id = request.headers.get("Admin-ID")
        if not admin_id:
            return False

        try:
            admin = Admin.objects.get(id=admin_id)
            request.admin = admin
        except Admin.DoesNotExist:
            return False

        # Try fetching AdminUser
        admin_user = None
        try:
            admin_user = request.user.admin_users.get(admin_id=admin_id)
        except AdminUser.DoesNotExist:
            # If user is super admin for any admin, allow
            if AdminUser.objects.filter(user=request.user, is_super_admin=True).exists():
                request.admin_user = AdminUser.objects.filter(user=request.user, is_super_admin=True).first()
                return True
            return False

        request.admin_user = admin_user
        return True
