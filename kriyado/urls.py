from django.urls import include, path

urlpatterns = [
    path("o/", include("oauth2_provider.urls", namespace="oauth2_provider")),
    path("api/v1/", include("apps.urls")),
]
