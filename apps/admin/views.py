from rest_framework import generics, status, permissions
from rest_framework.response import Response

from apps.admin.models import Admin, AdminUserRole
from apps.admin.permissions import HasAdminPermission
from apps.admin.serializer import (AdminSerializer, AdminApproveSerializer, AdminUserRoleSerializer,
                                   AdminUserSerializer)
from django.db import transaction
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from apps.account.models import User
from apps.admin.models import Admin, AdminUser
from apps.admin.serializer import AdminSerializer

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from apps.admin.models import Admin, AdminUser
from apps.admin.serializer import AdminSerializer

class CreateSuperAdminAPIView(generics.CreateAPIView):
    serializer_class = AdminSerializer
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        user = request.user
        name = request.data.get("name", f"Super Admin - {getattr(user, 'username', user.id)}")

        # ✅ 1. Get or create Admin for this user
        admin, created = Admin.objects.get_or_create(
            created_by=user,
            defaults={"name": name, "active": True},
        )

        # ✅ 2. If admin already existed, update name or activate it
        if not created:
            admin.name = name
            admin.active = True
            admin.save(update_fields=["name", "active"])

        # ✅ 3. Ensure AdminUser link exists and is marked super admin
        admin_user, link_created = AdminUser.objects.get_or_create(
            user=user,
            admin=admin,
            defaults={"is_super_admin": True},
        )

        # If link already existed but is_super_admin is False → fix it
        if not link_created and not admin_user.is_super_admin:
            admin_user.is_super_admin = True
            admin_user.save(update_fields=["is_super_admin"])

        # ✅ 4. Return clean response
        return Response(
            {
                "message": "Super Admin is active and linked successfully.",
                "data": AdminSerializer(admin).data,
                "admin_created": created,
                "link_created": link_created,
            },
            status=status.HTTP_201_CREATED if created or link_created else status.HTTP_200_OK,
        )

class SignupAdminAPIView(generics.CreateAPIView):
    serializer_class = AdminSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user

        admin, created = Admin.objects.get_or_create(
            created_by=user,
            defaults={
                "name": request.data.get("name", f"Admin - {user.username}"),
                "active": False,  # pending verification
            },
        )

        if not created:
            return Response(
                {
                    "message": "Admin already exists for this user. Await verification.",
                    "data": AdminSerializer(admin).data,
                    "already_existed": True,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "message": "Admin created. Await verification.",
                "data": AdminSerializer(admin).data,
                "already_existed": False,
            },
            status=status.HTTP_201_CREATED,
        )


class PendingAdminListAPIView(generics.ListAPIView):
    serializer_class = AdminSerializer
    permission_classes = [permissions.IsAuthenticated, HasAdminPermission]

    def get_queryset(self):
        return Admin.objects.filter(active=False)


class ApproveAdminAPIView(generics.UpdateAPIView):
    queryset = Admin.objects.all()
    serializer_class = AdminApproveSerializer
    permission_classes = [permissions.IsAuthenticated, HasAdminPermission]
    lookup_field = "id"

    def update(self, request, *args, **kwargs):
        admin = self.get_object()
        admin.active = True
        admin.save()
        return Response({"message": "Admin approved.", "data": AdminSerializer(admin).data})


class RejectAdminAPIView(generics.DestroyAPIView):
    queryset = Admin.objects.all()
    permission_classes = [permissions.IsAuthenticated, HasAdminPermission]
    lookup_field = "id"

    def destroy(self, request, *args, **kwargs):
        admin = self.get_object()
        admin.delete()
        return Response({"message": "Admin rejected/deleted."}, status=status.HTTP_204_NO_CONTENT)


class AdminUserRoleCreateAPIView(generics.CreateAPIView):
    serializer_class = AdminUserRoleSerializer
    permission_classes = [permissions.IsAuthenticated, HasAdminPermission]

    def perform_create(self, serializer):
        serializer.save(admin=self.request.admin)


class AdminUserRoleListAPIView(generics.ListAPIView):
    serializer_class = AdminUserRoleSerializer
    permission_classes = [permissions.IsAuthenticated, HasAdminPermission]

    def get_queryset(self):
        return AdminUserRole.objects.filter(admin=self.request.admin)


class AdminUserRoleUpdateAPIView(generics.UpdateAPIView):
    serializer_class = AdminUserRoleSerializer
    permission_classes = [permissions.IsAuthenticated, HasAdminPermission]
    lookup_field = "id"

    def get_queryset(self):
        return AdminUserRole.objects.filter(admin=self.request.admin)


class AdminUserRoleDeleteAPIView(generics.DestroyAPIView):
    serializer_class = AdminUserRoleSerializer
    permission_classes = [permissions.IsAuthenticated, HasAdminPermission]
    lookup_field = "id"

    def get_queryset(self):
        return AdminUserRole.objects.filter(admin=self.request.admin)


# 6️⃣ AdminUser (Assign Role)
class AdminUserCreateAPIView(generics.CreateAPIView):
    serializer_class = AdminUserSerializer
    permission_classes = [permissions.IsAuthenticated, HasAdminPermission]

    def perform_create(self, serializer):
        serializer.save(admin=self.request.admin)
