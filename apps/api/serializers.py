from rest_framework import serializers

from apps.cars.models import BodyType, Car, CarColor, CarImage
from apps.leads.forms import validate_test_drive_date
from apps.leads.models import TestDriveRequest, normalize_phone, uz_phone_validator


class BodyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BodyType
        fields = ["id", "name", "slug", "shape"]


class CarColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarColor
        fields = ["name", "hex_code"]


class CarImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarImage
        fields = ["image", "caption"]


class CarListSerializer(serializers.ModelSerializer):
    body_type = serializers.SlugRelatedField(slug_field="slug", read_only=True)
    powertrain_display = serializers.CharField(source="get_powertrain_display", read_only=True)
    url = serializers.HyperlinkedIdentityField(view_name="api:car-detail", lookup_field="slug")

    class Meta:
        model = Car
        fields = [
            "id", "url", "name", "slug", "tagline", "body_type", "powertrain",
            "powertrain_display", "price", "old_price", "range_km", "power_hp",
            "acceleration", "main_image", "accent_color",
        ]


class CarDetailSerializer(CarListSerializer):
    body_type = BodyTypeSerializer(read_only=True)
    drive_display = serializers.CharField(source="get_drive_display", read_only=True)
    colors = CarColorSerializer(many=True, read_only=True)
    images = CarImageSerializer(many=True, read_only=True)

    class Meta(CarListSerializer.Meta):
        fields = CarListSerializer.Meta.fields + [
            "description", "drive", "drive_display", "year", "electric_range_km",
            "battery_kwh", "torque_nm", "top_speed", "seats", "fast_charge_kw",
            "charge_time_min", "length_mm", "width_mm", "height_mm", "wheelbase_mm",
            "trunk_l", "colors", "images",
        ]


class TestDriveRequestSerializer(serializers.ModelSerializer):
    car = serializers.SlugRelatedField(slug_field="slug", queryset=Car.objects.available())
    phone = serializers.CharField(max_length=32)

    class Meta:
        model = TestDriveRequest
        fields = ["id", "car", "full_name", "phone", "preferred_date", "time_slot", "comment", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate_phone(self, value):
        value = normalize_phone(value)
        uz_phone_validator(value)
        return value

    def validate_preferred_date(self, value):
        validate_test_drive_date(value)  # Django ValidationError'ni DRF o'zi 400 ga aylantiradi
        return value
