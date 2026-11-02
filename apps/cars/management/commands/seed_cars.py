"""
Demo katalogni to'ldiradi: `python manage.py seed_cars`

Xususiyatlar ochiq manbalardagi taxminiy qiymatlar, narxlar esa namunaviy —
haqiqiy salon narxlari bilan admin paneldan almashtiring.
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.cars.models import BodyType, Car, CarColor
from apps.core.models import SalonInfo

BODY_TYPES = [
    ("Xetchbek", "hatchback", BodyType.Shape.HATCHBACK, 1),
    ("Sedan", "sedan", BodyType.Shape.SEDAN, 2),
    ("Krossover", "crossover", BodyType.Shape.SUV, 3),
    ("SUV", "suv", BodyType.Shape.SUV, 4),
]

PALETTE = {
    "oq": ("Oq marvarid", "#f2f2f0"),
    "qora": ("Kosmik qora", "#16181d"),
    "kulrang": ("Atlantis kulrang", "#6b7380"),
    "kok": ("Okean ko'k", "#1f5fa8"),
    "yashil": ("Aurora yashil", "#4f8a6e"),
    "qizil": ("Olovli qizil", "#b3132b"),
    "pushti": ("Atirgul", "#e4a3a9"),
}

CARS = [
    {
        "name": "BYD Seagull", "body": "hatchback", "powertrain": "ev", "drive": "fwd",
        "tagline": "Shahar uchun ixcham va tejamkor elektromobil",
        "price": 14900, "old_price": 16500,
        "range_km": 405, "battery_kwh": "38.9", "power_hp": 75, "torque_nm": 135,
        "acceleration": "13.0", "top_speed": 130, "seats": 4, "fast_charge_kw": 40,
        "charge_time_min": 30, "length_mm": 3780, "width_mm": 1715, "height_mm": 1540,
        "wheelbase_mm": 2500, "trunk_l": 230, "accent": "#4f8a6e", "featured": True,
        "colors": ["yashil", "oq", "pushti", "qora"],
        "description": (
            "Seagull — tor ko'chalar va to'xtash joyi kam bo'lgan shahar hayoti uchun yaratilgan. "
            "Blade batareyasi xavfsizligi, 12.8 dyuymli aylanuvchi ekran va arzon ekspluatatsiya "
            "uni birinchi elektromobil sifatida ideal tanlovga aylantiradi."
        ),
    },
    {
        "name": "BYD Dolphin", "body": "hatchback", "powertrain": "ev", "drive": "fwd",
        "tagline": "Keng salon va zamonaviy texnologiyalar",
        "price": 23900,
        "range_km": 427, "battery_kwh": "60.4", "power_hp": 204, "torque_nm": 310,
        "acceleration": "7.0", "top_speed": 160, "seats": 5, "fast_charge_kw": 88,
        "charge_time_min": 29, "length_mm": 4290, "width_mm": 1770, "height_mm": 1570,
        "wheelbase_mm": 2700, "trunk_l": 345, "accent": "#1f5fa8", "featured": True,
        "colors": ["kok", "oq", "kulrang", "pushti"],
        "description": (
            "Dolphin e-Platform 3.0 asosida qurilgan: tekis pol, 2.7 metrli baza va "
            "o'z sinfidagi eng keng orqa qator. Issiqlik nasosi qishda ham zapas yurishni saqlaydi."
        ),
    },
    {
        "name": "BYD Chazor", "body": "sedan", "powertrain": "dmi", "drive": "fwd",
        "tagline": "O'zbekistonda ishlab chiqarilgan gibrid sedan",
        "price": 19900,
        "range_km": 1000, "electric_range_km": 55, "battery_kwh": "8.3", "power_hp": 180,
        "torque_nm": 325, "acceleration": "7.9", "top_speed": 185, "seats": 5,
        "length_mm": 4765, "width_mm": 1837, "height_mm": 1495, "wheelbase_mm": 2718,
        "trunk_l": 450, "accent": "#6b7380", "featured": True,
        "colors": ["kulrang", "oq", "qora"],
        "description": (
            "DM-i super gibrid texnologiyasi: shahar ichida asosan elektrda, trassada esa "
            "1.5 litrli yuqori samarali dvigatel yordamida. 100 km ga ~3.8 litr yoqilg'i."
        ),
    },
    {
        "name": "BYD Song Plus DM-i", "body": "crossover", "powertrain": "dmi", "drive": "fwd",
        "tagline": "Oila uchun tejamkor gibrid krossover",
        "price": 29900,
        "range_km": 1100, "electric_range_km": 110, "battery_kwh": "18.3", "power_hp": 197,
        "torque_nm": 325, "acceleration": "8.5", "top_speed": 170, "seats": 5,
        "fast_charge_kw": 18, "length_mm": 4775, "width_mm": 1890, "height_mm": 1670,
        "wheelbase_mm": 2765, "trunk_l": 574, "accent": "#8a1c2b", "featured": True,
        "colors": ["qizil", "oq", "qora", "kulrang"],
        "description": (
            "Song Plus — keng yukxona, panoramik tom va 110 km gacha toza elektr yurish. "
            "Benzin bilan birga umumiy zapas 1100 km ga yetadi — uzoq safarlar uchun qulay."
        ),
    },
    {
        "name": "BYD Atto 3", "body": "crossover", "powertrain": "ev", "drive": "fwd",
        "tagline": "Dinamik dizaynli elektr krossover",
        "price": 27900, "old_price": 29900,
        "range_km": 420, "battery_kwh": "60.5", "power_hp": 204, "torque_nm": 310,
        "acceleration": "7.3", "top_speed": 160, "seats": 5, "fast_charge_kw": 88,
        "charge_time_min": 29, "length_mm": 4455, "width_mm": 1875, "height_mm": 1615,
        "wheelbase_mm": 2720, "trunk_l": 440, "accent": "#2d7f8f",
        "colors": ["kok", "oq", "kulrang"],
        "description": (
            "Atto 3 — sport ilhomidagi interyer, 5 yulduzli Euro NCAP xavfsizlik reytingi va "
            "kundalik foydalanish uchun ideal o'lchamlar."
        ),
    },
    {
        "name": "BYD Seal", "body": "sedan", "powertrain": "ev", "drive": "awd",
        "tagline": "3.8 soniyada 100 km/soat — sport sedan",
        "price": 41900,
        "range_km": 520, "battery_kwh": "82.5", "power_hp": 530, "torque_nm": 670,
        "acceleration": "3.8", "top_speed": 180, "seats": 5, "fast_charge_kw": 150,
        "charge_time_min": 26, "length_mm": 4800, "width_mm": 1875, "height_mm": 1460,
        "wheelbase_mm": 2920, "trunk_l": 400, "accent": "#c8102e", "featured": True,
        "colors": ["qizil", "kok", "oq", "qora"],
        "description": (
            "Seal CTB (Cell-to-Body) texnologiyasi bilan qurilgan: batareya kuzovning bir qismi, "
            "bu esa qattiqlik va boshqaruvni oshiradi. Ikki motorli to'liq privod — 530 o.k."
        ),
    },
    {
        "name": "BYD Han", "body": "sedan", "powertrain": "ev", "drive": "awd",
        "tagline": "Flagman biznes-sedan",
        "price": 44900,
        "range_km": 605, "battery_kwh": "85.4", "power_hp": 517, "torque_nm": 700,
        "acceleration": "3.9", "top_speed": 185, "seats": 5, "fast_charge_kw": 120,
        "charge_time_min": 30, "length_mm": 4995, "width_mm": 1910, "height_mm": 1495,
        "wheelbase_mm": 2920, "trunk_l": 410, "accent": "#3a3f4b",
        "colors": ["qora", "kulrang", "oq"],
        "description": (
            "Han — BYD ning flagman sedani: Nappa charm o'rindiqlar, Dynaudio audio tizimi, "
            "massajli va ventilyatsiyali o'rindiqlar hamda 600 km dan ortiq zapas yurish."
        ),
    },
    {
        "name": "BYD Tang", "body": "suv", "powertrain": "ev", "drive": "awd",
        "tagline": "7 o'rindiqli premium elektr SUV",
        "price": 54900,
        "range_km": 530, "battery_kwh": "108.8", "power_hp": 517, "torque_nm": 680,
        "acceleration": "4.6", "top_speed": 180, "seats": 7, "fast_charge_kw": 170,
        "charge_time_min": 30, "length_mm": 4900, "width_mm": 1950, "height_mm": 1725,
        "wheelbase_mm": 2820, "trunk_l": 940, "accent": "#24324a", "featured": True,
        "colors": ["qora", "kok", "oq", "kulrang"],
        "description": (
            "Tang — katta oila uchun: uch qator o'rindiq, to'liq privod va 108.8 kVt·soatlik "
            "Blade batareya. Tog'li yo'llarda ham ishonchli."
        ),
    },
]


class Command(BaseCommand):
    help = "Demo avtomobillar katalogini yaratadi yoki yangilaydi."

    @transaction.atomic
    def handle(self, *args, **options):
        SalonInfo.load()
        bodies = {}
        for name, slug, shape, order in BODY_TYPES:
            bodies[slug], _ = BodyType.objects.update_or_create(
                slug=slug, defaults={"name": name, "shape": shape, "order": order}
            )

        for index, data in enumerate(CARS, start=1):
            data = dict(data)
            colors = data.pop("colors")
            name = data.pop("name")
            data.update(
                body_type=bodies[data.pop("body")],
                accent_color=data.pop("accent"),
                is_featured=data.pop("featured", False),
                order=index,
            )
            car, created = Car.objects.update_or_create(name=name, defaults=data)
            car.colors.all().delete()
            CarColor.objects.bulk_create(
                CarColor(car=car, name=PALETTE[c][0], hex_code=PALETTE[c][1]) for c in colors
            )
            self.stdout.write(f"{'+' if created else '~'} {car.name}")

        self.stdout.write(self.style.SUCCESS(f"Tayyor: {len(CARS)} ta model."))
