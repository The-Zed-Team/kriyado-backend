from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from serializer import *


class UserRegisterAPIView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            data={"message": "User created successfully"},
            status=status.HTTP_201_CREATED
        )


class ActivateUserAPIView(APIView):
    def get(self, request, token):
        if UserService.activate_user(token):
            return Response(
                data={"message": "Your account activated successfully"},
                status=status.HTTP_200_OK
            )
        return Response(
            data={"message": "Invalid or expired token"},
            status=status.HTTP_400_BAD_REQUEST
        )
