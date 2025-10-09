from rest_framework.routers import DefaultRouter

from apps.shared.views import CountryViewSet, StateViewSet, DistrictViewSet, DiscountViewSet

router = DefaultRouter()
router.register(r"location/countries", CountryViewSet, basename="country")
router.register(r"location/states", StateViewSet, basename="state")
router.register(r"location/districts", DistrictViewSet, basename="district")
router.register(r'discounts', DiscountViewSet, basename='discount')

urlpatterns = router.urls
