from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter()
router.register(r"packages", PackageViewSet, basename="package")
router.register(r"durations", DurationViewSet, basename="duration")

urlpatterns = [
    path("", include(router.urls)),
]
