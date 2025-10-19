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
    """
    Check if the user has a specific admin permission.
    """

    def has_permission(self, request, view):
        try:
            # Get Admin-ID from headers
            admin_id = request.headers.get("Admin-ID")
            if not admin_id:
                logger.warning(f"Admin-ID header missing for user {request.user.id}")
                return False

            # Fetch admin
            admin = Admin.objects.get(id=admin_id)
            logger.info(f"Fetched admin {admin.id} for user {request.user.id}")

            # Fetch admin_user linking this user to admin
            admin_user = request.user.admin_users.get(admin_id=admin_id)
            request.admin = admin
            request.admin_user = admin_user

            logger.info(
                f"User {request.user.id} is linked to admin {admin.id} with role id {admin_user.role_id}, super_admin={admin_user.is_super_admin}"
            )

            # Super admin bypasses all checks
            if admin_user.is_super_admin:
                logger.info(f"User {request.user.id} is super admin. Permission granted.")
                return True

            # TODO: handle specific permissions here if needed
            return True

        except Admin.DoesNotExist:
            logger.error(f"Admin with ID {admin_id} does not exist")
            return False
        except AdminUser.DoesNotExist:
            logger.error(
                f"User {request.user.id} is not linked to admin {admin_id} (AdminUser missing)"
            )
            return False
        except Exception as e:
            logger.exception(f"Unexpected error checking admin permission: {e}")
            return False
