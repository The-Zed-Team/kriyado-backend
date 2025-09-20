from django.urls import include, path

urlpatterns = [
    path("", include("apps.account.urls")),
    path("", include("apps.vendor.urls")),
]
