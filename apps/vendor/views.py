from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response

from serializer import *


class VendorCreateAPIView(generics.CreateAPIView):
    serializer_class = VendorProfileSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            data={"message": "Vendor profile created successfully"},
            status=status.HTTP_201_CREATED
        )
