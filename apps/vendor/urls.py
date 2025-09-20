from django.urls import path
from .views import VendorCreateAPIView, VendorOnboardingStatusAPIView

urlpatterns = [
    path("vendor/create/", VendorCreateAPIView.as_view(), name="vendor-create"),
    path(
        "vendor/onboarding-status/",
        VendorOnboardingStatusAPIView.as_view(),
        name="vendor-onboarding-status",
    ),
]
