from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
from .views import ShopTypeViewSet

# Router for ShopType ViewSet
router = DefaultRouter()
router.register(r"shop-types", ShopTypeViewSet, basename="shop_type")

# Base urlpatterns
urlpatterns = [
    path("", include(router.urls)),  # includes ShopType ViewSet endpoints
]

# Vendor profile routes
urlpatterns += [
    path("vendor/create/", views.VendorCreateAPIView.as_view(), name="vendor-create"),
    path(
        "vendor/onboarding-status/",
        views.VendorOnboardingStatusAPIView.as_view(),
        name="vendor-onboarding-status",
    ),
]

# Vendor branch routes
urlpatterns += [
    path("vendor/branches/", views.VendorBranchListAPIView.as_view(), name="branch-list"),
    path("vendor/branches/create/", views.VendorBranchCreateAPIView.as_view(), name="branch-create"),
    path("vendor/branches/<uuid:pk>/", views.VendorBranchDetailAPIView.as_view(), name="branch-detail"),
    path("vendor/branches/<uuid:pk>/update/", views.VendorBranchUpdateAPIView.as_view(), name="branch-update"),
    path("vendor/branches/<uuid:pk>/delete/", views.VendorBranchDeleteAPIView.as_view(), name="branch-delete"),
]
