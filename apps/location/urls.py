from django.urls import path

from apps.location.views import *

urlpatterns = [
    path("country/", CountryOptionsListAPIView.as_view(), name="country-option-list"),
    path("states/<uuid:country_id>/", StateOptionsListAPIView.as_view(), name="state-by-country-option-list"),
    path("districts/<uuid:state_id>/", DistrictOptionsListAPIView.as_view(), name="district-by-state-option-list"),
]
