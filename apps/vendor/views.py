from rest_framework import generics
from rest_framework import status
from rest_framework import views
from rest_framework.generics import get_object_or_404
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


class VendorBranchCreateAPIView(generics.CreateAPIView):
    """Create a new vendor branch"""

    serializer_class = VendorBranchSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"user": self.request.user})
        return context


class VendorBranchListAPIView(generics.ListAPIView):
    """List all branches for the logged-in vendor"""

    serializer_class = VendorBranchSerializer

    def get_queryset(self):
        return VendorBranch.objects.filter(vendor__user=self.request.user)


class VendorBranchDetailAPIView(generics.RetrieveAPIView):
    """Get details of a single branch"""

    serializer_class = VendorBranchSerializer

    def get_queryset(self):
        return VendorBranch.objects.filter(vendor__user=self.request.user)


class VendorBranchUpdateAPIView(generics.UpdateAPIView):
    """Update a vendor branch"""

    serializer_class = VendorBranchSerializer

    def get_queryset(self):
        return VendorBranch.objects.filter(vendor__user=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"user": self.request.user})
        return context


class VendorBranchDeleteAPIView(generics.DestroyAPIView):
    """Delete a vendor branch (soft delete since using SafeDeleteModel)"""

    serializer_class = VendorBranchSerializer

    def get_queryset(self):
        return VendorBranch.objects.filter(vendor__user=self.request.user)
