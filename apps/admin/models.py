import uuid

from django.db import models
from safedelete.models import SOFT_DELETE_CASCADE, SafeDeleteModel

from apps.account.models import User
from apps.admin.mangers import AdminUserRoleManager, AdminUserManager
from core.django.models.mixins import Timestamps


class Admin(SafeDeleteModel, Timestamps):
    _safedelete_policy = SOFT_DELETE_CASCADE

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    active = models.BooleanField(default=False)  # Admin verification status
    created_by = models.OneToOneField(User, on_delete=models.CASCADE, related_name="admin")

    def __str__(self):
        return self.name


class AdminUserRole(SafeDeleteModel, Timestamps):
    """
    Defines roles for vendor users, allowing role-based access control.
    """

    _safedelete_policy = SOFT_DELETE_CASCADE

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True, db_index=True
    )
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    admin = models.ForeignKey(Admin, on_delete=models.RESTRICT)
    acl = models.JSONField(default=dict, help_text="JSON field to store ACL data.")

    objects = models.Manager()
    custom_manager = AdminUserRoleManager()

    class Meta:
        unique_together = ("admin", "code")

    def __str__(self):
        return self.name


class AdminUser(SafeDeleteModel, Timestamps):
    """
    Links users to vendors, allowing multiple users to be associated with a single vendor.
    """

    _safedelete_policy = SOFT_DELETE_CASCADE

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True, db_index=True
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="admin_users"
    )
    admin = models.ForeignKey(
        Admin, on_delete=models.CASCADE, related_name="admin_users"
    )
    role = models.ForeignKey(
        AdminUserRole, on_delete=models.SET_NULL, null=True, blank=True
    )
    acl = models.JSONField(default=dict, help_text="JSON field to store ACL data.")
    is_super_admin = models.BooleanField(default=False)

    objects = models.Manager()  # default manager
    custom_manager = AdminUserManager()

    class Meta:
        unique_together = ("user", "admin")

    def __str__(self):
        return f"{self.user.username} - {self.admin.name}"
