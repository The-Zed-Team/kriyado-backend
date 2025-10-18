import re

import unicodedata
from django.core.exceptions import ObjectDoesNotExist
from django.db import models


class AdminUserRoleManager(models.Manager):
    def create(self, **kwargs):
        """
        Automatically generates 'code' from 'name' before saving.
        """
        name = kwargs.get("name")
        if name:
            name_normalized = unicodedata.normalize("NFKD", name)
            code = (
                re.sub(r"[^\w]+", "_", name_normalized, flags=re.UNICODE)
                .strip("_")
                .lower()
                .replace("__", "_")
            )
            kwargs["code"] = code
        return super().create(**kwargs)


class AdminUserManager(models.Manager):
    def create_admin_user(self, user, admin, role=None, acl=None, is_super_admin=False):
        """
        Creates an AdminUser instance with default ACL if not provided.
        """
        if acl is None:
            acl = {}  # You can customize default ACL here

        admin_user = self.model(
            user=user,
            admin=admin,
            role=role,
            acl=acl,
            is_super_admin=is_super_admin,
        )
        admin_user.save()
        return admin_user

    def check_permission(self, user, admin, raise_exception=True):
        """
        Checks if the user has permission for the given admin.
        Returns True/False or raises PermissionError.
        """
        try:
            admin_user = self.get(user=user, admin=admin)
            if admin_user.is_super_admin:
                return True

            # If you want to check role-based ACL, you can add logic here:
            # if admin_user.role and admin_user.role.acl.get("some_permission"):
            #     return True

            return True  # currently allows all non-super-admins, adjust as needed
        except ObjectDoesNotExist:
            if raise_exception:
                raise PermissionError("User does not have the required permission.")
            return False
