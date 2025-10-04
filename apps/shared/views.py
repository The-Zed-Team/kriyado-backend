from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny

from apps.shared.serializer import *


class CountryOptionsListAPIView(generics.ListAPIView):
    permission_classes = [AllowAny]
    authentication_classes = []  # disables all authentication
    queryset = Country.objects.all()
    serializer_class = CountrySerializer


class StateOptionsListAPIView(generics.ListAPIView):
    serializer_class = StateSerializer

    def get_queryset(self):
        country_id = self.kwargs.get("country_id")
        try:
            country = Country.objects.get(id=country_id)
        except ObjectDoesNotExist:
            raise NotFound("Country not found")
        return State.objects.filter(country=country)


class DistrictOptionsListAPIView(generics.ListAPIView):
    serializer_class = DistrictSerializer

    def get_queryset(self):
        state_id = self.kwargs.get("state_id")
        try:
            state = State.objects.get(id=state_id)
        except ObjectDoesNotExist:
            raise NotFound("State not found")
        return District.objects.filter(state=state)
