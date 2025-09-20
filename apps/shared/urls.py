from django.urls import path

from apps.shared.views import *

urlpatterns = [
    path(
        "location/country/",
        CountryOptionsListAPIView.as_view(),
        name="country-option-list",
    ),
    path(
        "location/states/<uuid:country_id>/",
        StateOptionsListAPIView.as_view(),
        name="state-by-country-option-list",
    ),
    path(
        "location/districts/<uuid:state_id>/",
        DistrictOptionsListAPIView.as_view(),
        name="district-by-state-option-list",
    ),
]
