from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

# Schema view
schema_view = get_schema_view(
    openapi.Info(
        title="Discount Management API",
        default_version="v1",
        description="API documentation for Discounts, Vendor Branches, and Total Bill Presets",
        contact=openapi.Contact(email="support@example.com"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny, ]
)

urlpatterns = [
    # OAuth URLs
    path("o/", include("oauth2_provider.urls", namespace="oauth2_provider")),

    # Your app API URLs
    path("api/v1/", include("apps.urls")),

    # Swagger / Redoc at base URL
    path("", schema_view.with_ui("swagger", cache_timeout=0), name="swagger-ui"),  # Base URL
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="redoc-ui"),
    path("swagger.json", schema_view.without_ui(cache_timeout=0), name="schema-json"),
]
