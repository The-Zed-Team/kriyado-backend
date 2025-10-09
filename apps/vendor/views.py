from django.utils import timezone
from rest_framework import generics
from rest_framework import status
from rest_framework import views
from rest_framework import viewsets
from rest_framework.decorators import action
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


class TotalBillPresetViewSet(viewsets.ModelViewSet):
    queryset = TotalBillPreset.objects.all()
    serializer_class = TotalBillPresetSerializer


# Discount CRUD + Approve/Reject
class DiscountViewSet(viewsets.ModelViewSet):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer

    @action(detail=True, methods=["post"], url_path="approve")
    def approve_discount(self, request, pk=None):
        discount = self.get_object()
        if not request.user.is_staff:
            return Response({"detail": "Only admins can approve discounts."}, status=status.HTTP_403_FORBIDDEN)

        action_type = request.data.get("action", "approve")  # "approve" or "reject"
        if action_type == "approve":
            discount.approval_status = "approved"
        elif action_type == "reject":
            discount.approval_status = "rejected"
        else:
            return Response({"detail": "Invalid action. Use 'approve' or 'reject'."},
                            status=status.HTTP_400_BAD_REQUEST)

        discount.approved_by = request.user
        discount.approved_at = timezone.now()
        discount.save()
        serializer = self.get_serializer(discount)
        return Response(serializer.data)
