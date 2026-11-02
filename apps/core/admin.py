from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse

from .models import SalonInfo

admin.site.site_header = "BYD Salon — boshqaruv paneli"
admin.site.site_title = "BYD Salon"
admin.site.index_title = "Boshqaruv"


@admin.register(SalonInfo)
class SalonInfoAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["name", "slogan"]}),
        ("Aloqa", {"fields": [
            ("phone", "phone_secondary"), "email", "address", "working_hours", "map_embed_url",
        ]}),
        ("Ijtimoiy tarmoqlar", {"fields": ["telegram", "instagram"]}),
        ("Moliya", {"fields": [("usd_rate", "credit_rate")]}),
    ]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = SalonInfo.load()
        return redirect(reverse("admin:core_saloninfo_change", args=[obj.pk]))
