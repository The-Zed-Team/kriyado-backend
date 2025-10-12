from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views
from .views import (
    ShopTypeViewSet,
    VendorBranchViewSet,
)

router = DefaultRouter()
router.register(r"vendor/shop-types", ShopTypeViewSet, basename="shop_type")
router.register(r"vendor/branches", VendorBranchViewSet, basename="vendor-branch")


urlpatterns = [
    *router.urls,
    path("vendor/create/", views.VendorCreateAPIView.as_view(), name="vendor-create"),
    path("vendor/update/", views.VendorUpdateAPIView.as_view(), name="vendor-update"),
    path(
        "vendor/onboarding-status/",
        views.VendorOnboardingStatusAPIView.as_view(),
        name="vendor-onboarding-status",
    ),
    path("vendor/details/", views.VendorDetailAPIView.as_view(), name="vendor-details"),
    path(
        "vendor/branch_profile/",
        views.VendorBranchProfileViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
            }
        ),
        name="vendor-branch-profile",
    ),
    path(
        "vendor/users/",
        views.VendorUserInviteViewSet.as_view(
            {
                "get": "list",
                "post": "create",
                "delete": "destroy",
            }
        ),
        name="vendor-users",
    ),
]
