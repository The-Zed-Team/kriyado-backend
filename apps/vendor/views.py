from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets, views

from .serializer import CreateVendorSerializer


class VendorCreateAPIView(generics.CreateAPIView):
    serializer_class = CreateVendorSerializer

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
