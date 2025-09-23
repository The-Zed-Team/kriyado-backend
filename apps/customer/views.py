from rest_framework import viewsets

from apps.customer.serializer import *


class PackageViewSet(viewsets.ModelViewSet):
    queryset = Package.objects.all()
    serializer_class = PackageSerializer


class DurationViewSet(viewsets.ModelViewSet):
    queryset = Duration.objects.all()
    serializer_class = DurationSerializer
