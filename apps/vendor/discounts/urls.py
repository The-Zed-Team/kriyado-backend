from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

router.register(
    r"vendor/discounts",
    views.VendorBranchDiscountViewSet,
    basename="vendor-branch-discount",
)
router.register(r"categories", views.CategoryViewSet, basename="category")
router.register(
    r"discount-presets", views.DiscountPresetViewSet, basename="discount-preset"
)

urlpatterns = []

urlpatterns += [
    *router.urls,
]
