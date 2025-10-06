from rest_framework import generics, viewsets
from rest_framework import status
from rest_framework import views
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

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

    def get_object(self):
        # Ensure only the logged-in user's vendor can be updated
        return get_object_or_404(Vendor, user=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"user": self.request.user})
        return context


class VendorOnboardingStatusAPIView(views.APIView):

    def get(self, request, *args, **kwargs):
        vendor = request.user.vendor
        is_onboarded, step_status = vendor.update_vendor_onboarding_status()
        return Response(
            {
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

    def get_queryset(self):
        # Only branches belonging to the logged-in vendor
        return VendorBranch.objects.filter(vendor__user=self.request.user)

    def perform_create(self, serializer):
        # Automatically assign vendor from the logged-in user
        vendor = self.request.user.vendor
        serializer.save(vendor=vendor)

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

    def get_object(self):
        return Vendor.objects.get(user=self.request.user)
