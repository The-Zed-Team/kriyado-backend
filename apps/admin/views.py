from rest_framework import generics, status, permissions
from rest_framework.response import Response

from apps.admin.models import Admin, AdminUserRole
from apps.admin.permissions import HasAdminPermission
from apps.admin.serializer import (AdminSerializer, AdminApproveSerializer, AdminUserRoleSerializer,
                                   AdminUserSerializer)


class SignupAdminAPIView(generics.CreateAPIView):
    queryset = Admin.objects.all()
    serializer_class = AdminSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        admin = serializer.save(created_by=request.user)
        return Response({"message": "Admin created. Await verification.", "data": AdminSerializer(admin).data},
                        status=status.HTTP_201_CREATED)


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
