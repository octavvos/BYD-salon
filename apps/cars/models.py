from decimal import Decimal

from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

hex_color_validator = RegexValidator(r"^#[0-9a-fA-F]{6}$", "Rang #RRGGBB formatida bo'lishi kerak.")


class BodyType(models.Model):
    class Shape(models.TextChoices):
        HATCHBACK = "hatchback", "Xetchbek"
        SEDAN = "sedan", "Sedan"
        SUV = "suv", "Krossover / SUV"

    name = models.CharField("Nomi", max_length=60, unique=True)
    slug = models.SlugField(unique=True)
    shape = models.CharField(
        "Siluet", max_length=20, choices=Shape.choices, default=Shape.SEDAN,
        help_text="Rasm bo'lmaganda chiziladigan siluet turi.",
    )
    order = models.PositiveSmallIntegerField("Tartib", default=0)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Kuzov turi"
        verbose_name_plural = "Kuzov turlari"

    def __str__(self) -> str:
        return self.name


class CarQuerySet(models.QuerySet):
    def available(self):
        return self.filter(is_available=True)

    def featured(self):
        return self.available().filter(is_featured=True)

    def filter_by_params(self, params):
        """GET parametrlari bo'yicha filtr — sayt va API uchun umumiy."""
        qs = self
        if body := params.get("body"):
            qs = qs.filter(body_type__slug=body)
        if powertrain := params.get("powertrain"):
            qs = qs.filter(powertrain=powertrain)
        if q := params.get("q", "").strip():
            qs = qs.filter(models.Q(name__icontains=q) | models.Q(tagline__icontains=q))
        for param, lookup in (("price_min", "price__gte"), ("price_max", "price__lte")):
            value = params.get(param)
            if value:
                try:
                    qs = qs.filter(**{lookup: Decimal(value)})
                except ArithmeticError:
                    pass
        return qs


class Car(models.Model):
    class Powertrain(models.TextChoices):
        EV = "ev", "Elektr (EV)"
        DMI = "dmi", "Gibrid (DM-i)"

    class Drive(models.TextChoices):
        FWD = "fwd", "Old privod"
        RWD = "rwd", "Orqa privod"
        AWD = "awd", "To'liq privod"

    name = models.CharField("Model nomi", max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    tagline = models.CharField("Qisqa tavsif", max_length=160, blank=True)
    description = models.TextField("Batafsil tavsif", blank=True)
    body_type = models.ForeignKey(
        BodyType, on_delete=models.PROTECT, related_name="cars", verbose_name="Kuzov turi"
    )
    powertrain = models.CharField(
        "Dvigatel turi", max_length=10, choices=Powertrain.choices, default=Powertrain.EV
    )
    drive = models.CharField("Privod", max_length=10, choices=Drive.choices, default=Drive.FWD)
    year = models.PositiveSmallIntegerField("Yili", default=2026)
    price = models.DecimalField(
        "Narxi (USD)", max_digits=10, decimal_places=0, validators=[MinValueValidator(0)]
    )
    old_price = models.DecimalField(
        "Eski narx (USD)", max_digits=10, decimal_places=0, null=True, blank=True,
        help_text="Chegirma bo'lsa to'ldiring.",
    )

    # Texnik xususiyatlar
    range_km = models.PositiveIntegerField("Zapas yurish (km)")
    electric_range_km = models.PositiveIntegerField(
        "Faqat elektrda yurish (km)", null=True, blank=True, help_text="Gibridlar uchun."
    )
    battery_kwh = models.DecimalField("Batareya (kVt·soat)", max_digits=5, decimal_places=1)
    power_hp = models.PositiveIntegerField("Quvvat (o.k.)")
    torque_nm = models.PositiveIntegerField("Burovchi moment (N·m)")
    acceleration = models.DecimalField("0–100 km/soat (s)", max_digits=4, decimal_places=1)
    top_speed = models.PositiveIntegerField("Maks. tezlik (km/soat)")
    seats = models.PositiveSmallIntegerField("O'rindiqlar", default=5)
    fast_charge_kw = models.PositiveIntegerField("Tez quvvatlash (kVt)", null=True, blank=True)
    charge_time_min = models.PositiveIntegerField(
        "30→80% quvvatlash (daq)", null=True, blank=True
    )
    length_mm = models.PositiveIntegerField("Uzunligi (mm)", null=True, blank=True)
    width_mm = models.PositiveIntegerField("Kengligi (mm)", null=True, blank=True)
    height_mm = models.PositiveIntegerField("Balandligi (mm)", null=True, blank=True)
    wheelbase_mm = models.PositiveIntegerField("G'ildirak bazasi (mm)", null=True, blank=True)
    trunk_l = models.PositiveIntegerField("Yukxona (l)", null=True, blank=True)

    main_image = models.ImageField("Asosiy rasm", upload_to="cars/", blank=True)
    accent_color = models.CharField(
        "Aksent rang", max_length=7, default="#c8102e", validators=[hex_color_validator],
        help_text="Rasm bo'lmaganda siluet shu rangda chiziladi.",
    )
    is_featured = models.BooleanField("Bosh sahifada", default=False)
    is_available = models.BooleanField("Sotuvda", default=True)
    order = models.PositiveSmallIntegerField("Tartib", default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CarQuerySet.as_manager()

    class Meta:
        ordering = ["order", "price"]
        verbose_name = "Avtomobil"
        verbose_name_plural = "Avtomobillar"

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse("cars:detail", kwargs={"slug": self.slug})

    @property
    def discount_percent(self) -> int | None:
        if self.old_price and self.old_price > self.price:
            return round((1 - self.price / self.old_price) * 100)
        return None

    def price_uzs(self, usd_rate: int) -> int:
        return int(self.price * usd_rate)

    def key_specs(self) -> list[tuple[str, str]]:
        specs = [
            ("Zapas yurish", f"{self.range_km} km"),
            ("Quvvat", f"{self.power_hp} o.k."),
            ("0–100 km/soat", f"{self.acceleration} s"),
        ]
        if self.powertrain == self.Powertrain.DMI and self.electric_range_km:
            specs.append(("Elektrda", f"{self.electric_range_km} km"))
        else:
            specs.append(("Batareya", f"{self.battery_kwh} kVt·soat"))
        return specs

    def spec_groups(self) -> list[tuple[str, list[tuple[str, str]]]]:
        """Batafsil sahifadagi jadval uchun guruhlangan xususiyatlar (bo'shlari tashlanadi)."""

        def fmt(value, unit=""):
            return f"{value} {unit}".strip() if value not in (None, "") else None

        groups = [
            ("Dinamika", [
                ("Dvigatel turi", self.get_powertrain_display()),
                ("Privod", self.get_drive_display()),
                ("Quvvat", fmt(self.power_hp, "o.k.")),
                ("Burovchi moment", fmt(self.torque_nm, "N·m")),
                ("0–100 km/soat", fmt(self.acceleration, "s")),
                ("Maksimal tezlik", fmt(self.top_speed, "km/soat")),
            ]),
            ("Batareya va quvvatlash", [
                ("Batareya sig'imi", fmt(self.battery_kwh, "kVt·soat")),
                ("Umumiy zapas yurish", fmt(self.range_km, "km")),
                ("Faqat elektrda", fmt(self.electric_range_km, "km")),
                ("Tez quvvatlash (DC)", fmt(self.fast_charge_kw, "kVt")),
                ("30→80% quvvatlash", fmt(self.charge_time_min, "daqiqa")),
            ]),
            ("O'lchamlar", [
                ("Uzunlik", fmt(self.length_mm, "mm")),
                ("Kenglik", fmt(self.width_mm, "mm")),
                ("Balandlik", fmt(self.height_mm, "mm")),
                ("G'ildirak bazasi", fmt(self.wheelbase_mm, "mm")),
                ("Yukxona", fmt(self.trunk_l, "l")),
                ("O'rindiqlar soni", fmt(self.seats)),
            ]),
        ]
        return [
            (title, [(label, value) for label, value in rows if value])
            for title, rows in groups
        ]


class CarColor(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="colors")
    name = models.CharField("Rang nomi", max_length=60)
    hex_code = models.CharField("HEX", max_length=7, validators=[hex_color_validator])

    class Meta:
        verbose_name = "Rang"
        verbose_name_plural = "Ranglar"

    def __str__(self) -> str:
        return f"{self.car} — {self.name}"


class CarImage(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField("Rasm", upload_to="cars/gallery/")
    caption = models.CharField("Izoh", max_length=120, blank=True)
    order = models.PositiveSmallIntegerField("Tartib", default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Galereya rasmi"
        verbose_name_plural = "Galereya"

    def __str__(self) -> str:
        return self.caption or f"{self.car} #{self.pk}"
