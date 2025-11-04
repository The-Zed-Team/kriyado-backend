from django.db import transaction
from django.db.models import Q
from rest_framework import generics
from rest_framework import serializers
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

# from .serializer import *
from apps.account.models import AuthenticationProviders, User
from apps.account.serializer import UserInfoSerializer, SuperUserCreateSerializer
from apps.account.validator import FirebaseUserAuthenticationRequestSerializer
from apps.vendor.models import VendorBranchUser, VendorUser, VendorUserInvites
from core.authentication.firebase import firebase_client


# class UserRegisterAPIView(generics.CreateAPIView):
#     serializer_class = UserRegisterSerializer

#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(
#             data={"message": "User created successfully"},
#             status=status.HTTP_201_CREATED,
#         )


# class ActivateUserAPIView(APIView):
#     def get(self, request, token):
#         if UserService.activate_user(token):
#             return Response(
#                 data={"message": "Your account activated successfully"},
#                 status=status.HTTP_200_OK,
#             )
#         return Response(
#             data={"message": "Invalid or expired token"},
#             status=status.HTTP_400_BAD_REQUEST,
#         )

# =======================================
# class FirebaseUserAuthenticationView(APIView):
#     permission_classes = [AllowAny]
#     authentication_classes = []  # disables all authentication
#
#     @transaction.atomic
#     def post(self, request):
#         request_serializer = FirebaseUserAuthenticationRequestSerializer(
#             data=request.data
#         )
#         request_serializer.is_valid(raise_exception=True)
#         request_data = request_serializer.data
#
#         id_token = request_data["id_token"]
#         # only required if the provider is email
#         password = request_data.get("password")
#         first_name = request_data.get("first_name")
#         middle_name = request_data.get("middle_name")
#         last_name = request_data.get("last_name")
#
#         verification_response = firebase_client.verify_token(
#             id_token, fetch_user_info=True
#         )
#         if not verification_response.valid:
#             raise serializers.ValidationError(
#                 {"detail": "Authentication failed"}, code=401
#             )
#         firebase_user = verification_response.user
#
#         # Basic validation
#         if not firebase_user.email and not firebase_user.phone_number:
#             raise serializers.ValidationError(
#                 {"detail": "Invalid authentication credentials"}, code=400
#             )
#
#         if firebase_user.email and not firebase_user.email_verified:
#             raise serializers.ValidationError(
#                 {"detail": "Email not verified"}, code=400
#             )
#
#         # Collect providers
#         providers = [
#             {
#                 "provider": "firebase",
#                 "provider_uid": firebase_user.uid,
#                 "extra_data": {
#                     "photo_url": firebase_user.photo_url,
#                     "email": firebase_user.email,
#                     "display_name": firebase_user.display_name,
#                 },
#             }
#         ]
#         for provider_data in firebase_user.provider_data:
#             if provider_data.provider_id in ["google.com", "apple.com"]:
#                 providers.append(
#                     {
#                         "provider": (
#                             "google"
#                             if provider_data.provider_id == "google.com"
#                             else "apple"
#                         ),
#                         "provider_uid": provider_data.uid,
#                         "extra_data": {
#                             "photo_url": provider_data.photo_url,
#                             "email": provider_data.email,
#                             "display_name": provider_data.display_name,
#                             "firebase_uid": firebase_user.uid,
#                         },
#                     }
#                 )
#             elif provider_data.provider_id == "password":
#                 # email/password signup requires password & first_name
#                 if not firebase_user:
#                     if not password:
#                         raise serializers.ValidationError(
#                             {"password": "This field is required for email sign-in."},
#                             code=400,
#                         )
#                     if len(password) < 8:
#                         raise serializers.ValidationError(
#                             {"password": "Password must be at least 8 characters long."},
#                             code=400,
#                         )
#                     # if not first_name:
#                     #     raise serializers.ValidationError(
#                     #         {"first_name": "This field is required for email sign-in."},
#                     #         code=400,
#                     #     )
#             else:
#                 raise serializers.ValidationError(
#                     {"detail": f"Unsupported provider: {provider_data.provider_id}"},
#                     code=400,
#                 )
#
#         # Build user query
#         qs = Q()
#         if firebase_user.email:
#             qs |= Q(email=firebase_user.email)
#         if firebase_user.phone_number:
#             qs |= Q(phone_number=firebase_user.phone_number)
#
#         if not first_name and firebase_user.display_name:
#             first_name = firebase_user.display_name
#
#         user = User.objects.filter(qs).first()
#         create_user = bool(user is None)
#
#         if not user:
#             # Determine auth_provider for Django user
#             non_firebase_provider = next(
#                 (p["provider"] for p in providers if p["provider"] != "firebase"),
#                 "email",
#             )
#
#             user_data = {
#                 "email": firebase_user.email,
#                 "email_verified": firebase_user.email_verified,
#                 "phone_number": firebase_user.phone_number,
#                 "phone_verified": bool(firebase_user.phone_number),
#                 "password": password if non_firebase_provider == "email" else None,
#                 "first_name": first_name,
#                 "middle_name": middle_name or "",
#                 "last_name": last_name or "",
#                 "is_active": True,
#                 "auth_provider": non_firebase_provider,
#             }
#
#             user = User.objects.create_user(**user_data)
#
#             for provider in providers:
#                 AuthenticationProviders.objects.create(user=user, **provider)
#         invites = VendorUserInvites.objects.filter(email=user.email, status="pending")
#         for invite in invites:
#             invite.accept_invite(user)
#
#         vendor_users = VendorUser.objects.select_related("vendor").filter(user=user)
#         vendor_branch_users = VendorBranchUser.objects.select_related(
#             "vendor_branch__vendor"
#         ).filter(user=user)
#         vendor_accounts = {}
#         for u in vendor_users:
#             vendor_accounts[u.vendor_id] = {
#                 "display_name": u.vendor.name,
#                 "vendor_id": str(u.vendor.id),
#                 "vendor_user_id": str(u.id),
#                 "is_super_admin": u.is_super_admin,
#                 "has_vendor_account_access": True,
#                 "branches": [],
#             }
#
#         for u in vendor_branch_users:
#             if u.vendor_branch.vendor_id not in vendor_accounts:
#                 vendor_accounts[u.vendor_branch.vendor_id] = {
#                     "display_name": u.vendor_branch.vendor.name,
#                     "vendor_id": str(u.vendor_branch.vendor.id),
#                     "vendor_user_id": None,
#                     "is_super_admin": False,
#                     "has_vendor_account_access": False,
#                     "branches": [],
#                 }
#             vendor_accounts[u.vendor_branch.vendor_id]["branches"].append(
#                 {
#                     "display_name": f"{u.vendor_branch.vendor.name} ({u.vendor_branch.code}) ({u.vendor_branch.district.name})",
#                     "vendor_branch_id": str(u.vendor_branch.id),
#                     "vendor_branch_user_id": str(u.id),
#                     "is_super_admin": u.is_super_admin,
#                 }
#             )
#
#         return Response(
#             data={
#                 "id": str(user.id),
#                 "username": user.username,
#                 "email": user.email,
#                 "phone": user.phone_number,
#                 "first_name": user.first_name,
#                 "last_name": user.last_name,
#                 "email_verified": user.email_verified,
#                 "phone_verified": user.phone_verified,
#                 # "providers": providers,
#                 "new_user": create_user,
#                 "vendor_portal_accounts": vendor_accounts.values(),
#             },
#             status=status.HTTP_200_OK,
#         )
#
# ===========================================================================================
# class FirebaseUserAuthenticationView(APIView):
# permission_classes = [AllowAny]
# authentication_classes = []
#
# @transaction.atomic
# def post(self, request):
#     request_serializer = FirebaseUserAuthenticationRequestSerializer(
#         data=request.data
#     )
#     request_serializer.is_valid(raise_exception=True)
#     request_data = request_serializer.data
#
#     id_token = request_data["id_token"]
#     # below parameters are required only if the provider is email
#     password = request_data.get("password")
#     first_name = request_data.get("first_name")
#     middle_name = request_data.get("middle_name")
#     last_name = request_data.get("last_name")
#
#     verification_response = firebase_client.verify_token(
#         id_token, fetch_user_info=True
#     )
#     print(verification_response)
#     if not verification_response.valid:
#         raise serializers.ValidationError(
#             {"detail": "Authentication failed"}, code=401
#         )
#     firebase_user = verification_response.user
#
#     # perform basic validation on firebase user data
#
#     if not firebase_user.email and not firebase_user.phone_number:
#         raise serializers.ValidationError(
#             {"detail": "Invalid authentication credentials"}, code=400
#         )
#
#     if firebase_user.email and not firebase_user.email_verified:
#         raise serializers.ValidationError(
#             {"detail": "Email not verified"}, code=400
#         )
#
#     # check the user provders so that we can perform further validations on that.
#     providers = [
#         {
#             "provider": "firebase",
#             "provider_uid": firebase_user.uid,
#             "extra_data": {
#                 "photo_url": firebase_user.photo_url,
#                 "email": firebase_user.email,
#                 "display_name": firebase_user.display_name,
#             },
#         }
#     ]
#     for provider_data in firebase_user.provider_data:
#         if provider_data.provider_id == "google.com":
#             providers.append(
#                 {
#                     "provider": "google",
#                     "provider_uid": provider_data.uid,
#                     "extra_data": {
#                         "photo_url": provider_data.photo_url,
#                         "email": provider_data.email,
#                         "display_name": provider_data.display_name,
#                         "firebase_uid": firebase_user.uid,
#                     },
#                 }
#             )
#         elif provider_data.provider_id == "apple.com":
#             providers.append(
#                 {
#                     "provider": "apple",
#                     "provider_uid": provider_data.uid,
#                     "extra_data": {
#                         "photo_url": provider_data.photo_url,
#                         "email": provider_data.email,
#                         "display_name": provider_data.display_name,
#                         "firebase_uid": firebase_user.uid,
#                     },
#                 }
#             )
#         elif provider_data.provider_id == "password":
#             # provider is email, so the password param is required so that we can update the user password in our database
#             if not password:
#                 raise serializers.ValidationError(
#                     {"password": "This field is required for email sign-in."},
#                     code=400,
#                 )
#             if len(password) < 8:
#                 raise serializers.ValidationError(
#                     {"password": "Password must be at least 8 characters long."},
#                     code=400,
#                 )
#             if not first_name:
#                 raise serializers.ValidationError(
#                     {"first_name": "This field is required for email sign-in."},
#                     code=400,
#                 )
#         else:
#             raise serializers.ValidationError(
#                 {"detail": "Unsupported provider"}, code=400
#             )
#     qs = Q()
#     if firebase_user.email:
#         qs |= Q(email=firebase_user.email)
#     if firebase_user.phone_number:
#         qs |= Q(phone_number=firebase_user.phone_number)
#
#     if not first_name and firebase_user.display_name:
#         first_name = firebase_user.display_name
#
#     user = User.objects.filter(qs).first()
#     create_user = bool(user is None)
#
#     if not user:
#         user_data = {
#             "email": firebase_user.email,
#             "email_verified": firebase_user.email_verified,
#             "phone_number": firebase_user.phone_number,
#             "phone_verified": bool(firebase_user.phone_number),
#             "password": password,
#             "first_name": first_name,
#             "middle_name": middle_name or "",
#             "last_name": last_name or "",
#             "is_active": True,
#             "auth_provider": (
#                 providers[0]["provider"]
#                 if providers[0]["provider"] != "firebase"
#                 else "email"
#             ),
#         }
#
#         user = User.objects.create_user(**user_data)
#         for provider in providers:
#             AuthenticationProviders.objects.create(user=user, **provider)
#
#     return Response(
#         data={
#             "id": str(user.id),
#             "username": user.username,
#             "email": user.email,
#             "phone": user.phone_number,
#             "first_name": user.first_name,
#             "last_name": user.last_name,
#             "email_verified": user.email_verified,
#             "phone_verified": user.phone_verified,
#             "providers": providers,
#             "new_user": create_user,
#         },
#         status=status.HTTP_200_OK,
#     )


class FirebaseUserAuthenticationView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []  # disables all authentication

    @transaction.atomic
    def post(self, request):
        # Step 1: Validate incoming request
        request_serializer = FirebaseUserAuthenticationRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        request_data = request_serializer.data

        id_token = request_data["id_token"]
        password = request_data.get("password")
        first_name = request_data.get("first_name")
        middle_name = request_data.get("middle_name")
        last_name = request_data.get("last_name")

        # Step 2: Verify Firebase token
        verification_response = firebase_client.verify_token(id_token, fetch_user_info=True)
        if not verification_response.valid:
            raise serializers.ValidationError({"detail": "Authentication failed"}, code=401)

        firebase_user = verification_response.user

        # Step 3: Basic Firebase user validation
        if not firebase_user.email and not firebase_user.phone_number:
            raise serializers.ValidationError({"detail": "Invalid authentication credentials"}, code=400)

        if firebase_user.email and not firebase_user.email_verified:
            raise serializers.ValidationError({"detail": "Email not verified"}, code=400)

        # Step 4: Build query to find existing user
        qs = Q()
        if firebase_user.email:
            qs |= Q(email=firebase_user.email)
        if firebase_user.phone_number:
            qs |= Q(phone_number=firebase_user.phone_number)

        if not first_name and firebase_user.display_name:
            first_name = firebase_user.display_name

        user = User.objects.filter(qs).first()
        create_user = bool(user is None)

        # Step 5: Detect if user uses email/password provider
        uses_email_password = any(
            p.provider_id == "password" for p in firebase_user.provider_data
        )

        # ✅ Require password only if creating a new email/password user
        if create_user and uses_email_password:
            if not password:
                raise serializers.ValidationError(
                    {"password": "This field is required for email sign-up."}, code=400
                )
            if len(password) < 8:
                raise serializers.ValidationError(
                    {"password": "Password must be at least 8 characters long."}, code=400
                )

        # Step 6: Collect providers info
        providers = [
            {
                "provider": "firebase",
                "provider_uid": firebase_user.uid,
                "extra_data": {
                    "photo_url": firebase_user.photo_url,
                    "email": firebase_user.email,
                    "display_name": firebase_user.display_name,
                },
            }
        ]

        for provider_data in firebase_user.provider_data:
            if provider_data.provider_id in ["google.com", "apple.com"]:
                providers.append(
                    {
                        "provider": (
                            "google" if provider_data.provider_id == "google.com" else "apple"
                        ),
                        "provider_uid": provider_data.uid,
                        "extra_data": {
                            "photo_url": provider_data.photo_url,
                            "email": provider_data.email,
                            "display_name": provider_data.display_name,
                            "firebase_uid": firebase_user.uid,
                        },
                    }
                )
            elif provider_data.provider_id not in ["password", "firebase"]:
                raise serializers.ValidationError(
                    {"detail": f"Unsupported provider: {provider_data.provider_id}"},
                    code=400,
                )

        # Step 7: Create new user if not exists
        if not user:
            # Determine primary auth provider for Django user
            non_firebase_provider = next(
                (p["provider"] for p in providers if p["provider"] != "firebase"), "email"
            )

            user_data = {
                "email": firebase_user.email,
                "email_verified": firebase_user.email_verified,
                "phone_number": firebase_user.phone_number,
                "phone_verified": bool(firebase_user.phone_number),
                "password": password if non_firebase_provider == "email" else None,
                "first_name": first_name,
                "middle_name": middle_name or "",
                "last_name": last_name or "",
                "is_active": True,
                "auth_provider": non_firebase_provider,
            }

            user = User.objects.create_user(**user_data)

            for provider in providers:
                AuthenticationProviders.objects.create(user=user, **provider)

        # Step 8: Accept vendor invites if any
        invites = VendorUserInvites.objects.filter(email=user.email, status="pending")
        for invite in invites:
            invite.accept_invite(user)

        # Step 9: Collect vendor-related accounts
        vendor_users = VendorUser.objects.select_related("vendor").filter(user=user)
        vendor_branch_users = VendorBranchUser.objects.select_related("vendor_branch__vendor").filter(user=user)

        vendor_accounts = {}

        for u in vendor_users:
            vendor_accounts[u.vendor_id] = {
                "display_name": u.vendor.name,
                "vendor_id": str(u.vendor.id),
                "vendor_user_id": str(u.id),
                "is_super_admin": u.is_super_admin,
                "has_vendor_account_access": True,
                "branches": [],
            }

        for u in vendor_branch_users:
            if u.vendor_branch.vendor_id not in vendor_accounts:
                vendor_accounts[u.vendor_branch.vendor_id] = {
                    "display_name": u.vendor_branch.vendor.name,
                    "vendor_id": str(u.vendor_branch.vendor.id),
                    "vendor_user_id": None,
                    "is_super_admin": False,
                    "has_vendor_account_access": False,
                    "branches": [],
                }

            vendor_accounts[u.vendor_branch.vendor_id]["branches"].append(
                {
                    "display_name": f"{u.vendor_branch.vendor.name} ({u.vendor_branch.code}) ({u.vendor_branch.district.name})",
                    "vendor_branch_id": str(u.vendor_branch.id),
                    "vendor_branch_user_id": str(u.id),
                    "is_super_admin": u.is_super_admin,
                }
            )

        # Step 10: Return successful response
        return Response(
            data={
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "phone": user.phone_number,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email_verified": user.email_verified,
                "phone_verified": user.phone_verified,
                "new_user": create_user,
                "vendor_portal_accounts": vendor_accounts.values(),
            },
            status=status.HTTP_200_OK,
        )


class UserInfoView(generics.RetrieveAPIView):
    serializer_class = UserInfoSerializer

    def get_object(self):
        return self.request.user


class SuperUserCreateAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SuperUserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "id": str(user.id),
                    "username": user.username,
                    "email": user.email,
                    "phone_number": user.phone_number,
                    "message": "Superuser created successfully",
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
