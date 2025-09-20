from django.urls import path

from apps.account.views import (
    FirebaseUserAuthenticationView,
    UserInfoView,
)
from rest_framework.routers import SimpleRouter

router = SimpleRouter(trailing_slash=False)


urlpatterns = [
    path(
        r"account/user_info/",
        UserInfoView.as_view(),
        name="user-info",
    ),
    path(
        r"account/firebase_authenticate/",
        FirebaseUserAuthenticationView.as_view(),
        name="firebase-authenticate",
    ),
]
