from django.db import models


class SalonInfo(models.Model):
    """Salon haqidagi yagona (singleton) yozuv — admin paneldan tahrirlanadi."""

    name = models.CharField("Nomi", max_length=120, default="BYD Salon")
    slogan = models.CharField(
        "Shior", max_length=200, default="Kelajak elektromobillari — bugun Toshkentda"
    )
    phone = models.CharField("Telefon", max_length=32, default="+998 71 200 00 00")
    phone_secondary = models.CharField("Qo'shimcha telefon", max_length=32, blank=True)
    email = models.EmailField("Email", default="info@bydsalon.uz")
    address = models.CharField(
        "Manzil", max_length=255, default="Toshkent sh., Yunusobod tumani, Amir Temur ko'chasi"
    )
    working_hours = models.CharField(
        "Ish vaqti", max_length=120, default="Du–Sha: 09:00–20:00, Ya: 10:00–18:00"
    )
    map_embed_url = models.URLField(
        "Xarita (iframe src)",
        max_length=600,
        blank=True,
        help_text="Google/Yandex xaritadan olingan embed havola.",
    )
    telegram = models.URLField("Telegram", blank=True)
    instagram = models.URLField("Instagram", blank=True)
    usd_rate = models.PositiveIntegerField(
        "USD kursi (so'm)",
        default=12_800,
        help_text="Narxlarni so'mda taxminiy ko'rsatish uchun.",
    )
    credit_rate = models.DecimalField(
        "Kredit foizi (yillik, %)", max_digits=5, decimal_places=2, default=24
    )

    class Meta:
        verbose_name = "Salon ma'lumotlari"
        verbose_name_plural = "Salon ma'lumotlari"

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls) -> "SalonInfo":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
