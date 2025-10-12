from django.utils import timezone
from rest_framework import generics
from rest_framework import status
from rest_framework import views
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from core.authentication.permission_class import (
    HasVendorBranchPermission,
    HasVendorPermission,
)
from rest_framework import mixins

from .serializer import *


class VendorCreateAPIView(generics.CreateAPIView):
    serializer_class = CreateVendorSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"user": self.request.user})
        return context


class VendorUpdateAPIView(generics.UpdateAPIView):
    serializer_class = UpdateVendorSerializer
    queryset = Vendor.objects.all()
    permission_classes = [HasVendorPermission]

    def get_object(self):
        # Ensure only the logged-in user's vendor can be updated
        return self.request.vendor

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"user": self.request.user})
        return context


class VendorOnboardingStatusAPIView(views.APIView):
    permission_classes = [HasVendorPermission]

    def get(self, request, *args, **kwargs):
        vendor = request.vendor
        is_onboarded, step_status = vendor.update_vendor_onboarding_status()
        return Response(
            {
                "vendor_id": vendor.id,
                "default_branch_id": (
                    vendor.default_branch.id if vendor.default_branch else None
                ),
                "is_onboarded": is_onboarded,
                "step_status": step_status,
            },
            status=status.HTTP_200_OK,
        )


class VendorBranchViewSet(viewsets.ModelViewSet):
    """
    Full CRUD for VendorBranch, restricted to branches of logged-in vendor.
    Supports: list, retrieve, update, delete, create
    """

    serializer_class = VendorBranchSerializer
    permission_classes = [HasVendorPermission]

    def get_queryset(self):
        # Only branches belonging to the logged-in vendor
        return VendorBranch.objects.filter(vendor=self.request.vendor)

    def perform_create(self, serializer):
        # Automatically assign vendor from the logged-in user
        vendor = self.request.vendor
        serializer.save(vendor=vendor)
        self.request.vendor.update_vendor_onboarding_status()

    def perform_update(self, serializer):
        super().perform_update(serializer)
        self.request.vendor.update_vendor_onboarding_status()

    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        self.request.vendor.update_vendor_onboarding_status()


class ShopTypeViewSet(viewsets.ModelViewSet):
    """
    Full CRUD API for ShopType
    """

    permission_classes = [AllowAny]
    authentication_classes = []
    queryset = ShopType.objects.all().order_by("name")
    serializer_class = ShopTypeSerializer


class VendorDetailAPIView(generics.RetrieveAPIView):
    """
    Retrieve vendor info with profile, default branch, and all branches
    """

    serializer_class = VendorDetailSerializer
    permission_classes = [HasVendorPermission]

    def get_object(self):
        return self.request.vendor


class VendorBranchProfileViewSet(
    viewsets.GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
):
    queryset = VendorBranchProfile.objects.all()
    serializer_class = VendorBranchProfileSerializer
    permission_classes = [HasVendorBranchPermission]

    def get_object(self):
        return get_object_or_404(
            VendorBranchProfile, vendor_branch=self.request.vendor_branch
        )

    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        self.request.vendor_branch.vendor.update_vendor_onboarding_status()
        return response

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        self.request.vendor_branch.vendor.update_vendor_onboarding_status()
        return response


class VendorUserInviteViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
):
    queryset = VendorUserInvites.objects.all()
    serializer_class = VendorUserInviteSerializer
    permission_classes = [HasVendorPermission]

    def get_queryset(self):
        return VendorUserInvites.objects.filter(vendor=self.request.vendor)
