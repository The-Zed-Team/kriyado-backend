from rest_framework import serializers
from apps.admin.models import Admin, AdminUser, AdminUserRole

# Admin Serializer
class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = ["id", "name", "active"]
        read_only_fields = ["id", "active"]

# Serializer for Approve/Reject Admin
class AdminApproveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = ["active"]

# AdminUserRole Serializer
class AdminUserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminUserRole
        fields = ["id", "name", "description", "acl"]
        read_only_fields = ["id"]

# AdminUser Serializer (assign user to admin)
class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminUser
        fields = ["id", "user", "role", "acl", "is_super_admin"]
        read_only_fields = ["id"]
