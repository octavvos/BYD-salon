from django.contrib import admin
from django.utils.html import format_html

from .models import BodyType, Car, CarColor, CarImage


class CarColorInline(admin.TabularInline):
    model = CarColor
    extra = 1


class CarImageInline(admin.TabularInline):
    model = CarImage
    extra = 1
    fields = ["preview", "image", "caption", "order"]
    readonly_fields = ["preview"]

    @admin.display(description="Ko'rinish")
    def preview(self, obj):
        if obj.pk and obj.image:
            return format_html('<img src="{}" style="height:48px;border-radius:4px">', obj.image.url)
        return "—"


@admin.register(BodyType)
class BodyTypeAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "shape", "order"]
    list_editable = ["order"]
    prepopulated_fields = {"slug": ["name"]}


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = [
        "swatch", "name", "body_type", "powertrain", "price", "range_km",
        "is_featured", "is_available", "order",
    ]
    list_display_links = ["swatch", "name"]
    list_editable = ["price", "is_featured", "is_available", "order"]
    list_filter = ["body_type", "powertrain", "is_available", "is_featured"]
    search_fields = ["name", "tagline"]
    prepopulated_fields = {"slug": ["name"]}
    inlines = [CarColorInline, CarImageInline]
    fieldsets = [
        (None, {"fields": [
            "name", "slug", "tagline", "description", "body_type",
            ("powertrain", "drive", "year"),
        ]}),
        ("Narx", {"fields": [("price", "old_price")]}),
        ("Dinamika", {"fields": [
            ("power_hp", "torque_nm"), ("acceleration", "top_speed"),
        ]}),
        ("Batareya", {"fields": [
            ("battery_kwh", "range_km", "electric_range_km"),
            ("fast_charge_kw", "charge_time_min"),
        ]}),
        ("O'lchamlar", {"classes": ["collapse"], "fields": [
            ("length_mm", "width_mm", "height_mm"), ("wheelbase_mm", "trunk_l", "seats"),
        ]}),
        ("Ko'rinish", {"fields": [
            "main_image", "accent_color", ("is_featured", "is_available", "order"),
        ]}),
    ]

    @admin.display(description="")
    def swatch(self, obj):
        return format_html(
            '<span style="display:inline-block;width:14px;height:14px;border-radius:50%;background:{}"></span>',
            obj.accent_color,
        )
