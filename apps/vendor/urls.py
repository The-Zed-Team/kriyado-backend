from django.urls import path

from . import views

urlpatterns = [
    path("vendor/create/", views.VendorCreateAPIView.as_view(), name="vendor-create"),
    path(
        "vendor/onboarding-status/",
        views.VendorOnboardingStatusAPIView.as_view(),
        name="vendor-onboarding-status",
    ),
    path("vendor/branches/", views.VendorBranchListAPIView.as_view(), name="branch-list"),
    path("vendor/branches/create/", views.VendorBranchCreateAPIView.as_view(), name="branch-create"),
    path("vendor/branches/<uuid:pk>/", views.VendorBranchDetailAPIView.as_view(), name="branch-detail"),
    path("vendor/branches/<uuid:pk>/update/", views.VendorBranchUpdateAPIView.as_view(), name="branch-update"),
    path("vendor/branches/<uuid:pk>/delete/", views.VendorBranchDeleteAPIView.as_view(), name="branch-delete"),
]
