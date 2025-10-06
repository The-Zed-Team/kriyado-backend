# apps/location/admin.py

from django.contrib import admin
from .models import Country, State, District


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "updated_at")
    search_fields = ("name",)
    ordering = ("name",)
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ("name", "country", "created_at", "updated_at")
    search_fields = ("name", "country__name")
    list_filter = ("country",)
    ordering = ("country__name", "name")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ("name", "state", "created_at", "updated_at")
    search_fields = ("name", "state__name", "state__country__name")
    list_filter = ("state__country", "state")
    ordering = ("state__country__name", "state__name", "name")
    readonly_fields = ("id", "created_at", "updated_at")
