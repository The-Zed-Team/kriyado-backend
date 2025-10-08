from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from apps.shared.models import Country, State, District
from apps.shared.serializer import CountrySerializer, StateSerializer, DistrictSerializer

from apps.shared.serializer import *

class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [AllowAny]      # Public API
    authentication_classes = []          # Skip Firebase auth


class StateViewSet(viewsets.ModelViewSet):
    queryset = State.objects.all()
    serializer_class = StateSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def get_queryset(self):
        country_id = self.kwargs.get("country_id")
        if country_id:
            return self.queryset.filter(country_id=country_id)
        return self.queryset


class DistrictViewSet(viewsets.ModelViewSet):
    queryset = District.objects.all()
    serializer_class = DistrictSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def get_queryset(self):
        state_id = self.kwargs.get("state_id")
        if state_id:
            return self.queryset.filter(state_id=state_id)
        return self.queryset
