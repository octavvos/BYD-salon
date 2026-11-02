from django.core.validators import RegexValidator
from django.db import models

uz_phone_validator = RegexValidator(
    r"^\+998\d{9}$", "Telefon raqamni +998XXXXXXXXX formatida kiriting."
)


def normalize_phone(raw: str) -> str:
    """'+998 (90) 123-45-67', '90 123 45 67' kabi kiritishlarni +998901234567 ga keltiradi."""
    digits = "".join(ch for ch in raw if ch.isdigit())
    if len(digits) == 9:
        digits = "998" + digits
    return "+" + digits if digits else ""


class LeadStatus(models.TextChoices):
    NEW = "new", "Yangi"
    IN_PROGRESS = "in_progress", "Jarayonda"
    DONE = "done", "Yakunlangan"
    CANCELLED = "cancelled", "Bekor qilingan"


class BaseLead(models.Model):
    full_name = models.CharField("Ism familiya", max_length=120)
    phone = models.CharField("Telefon", max_length=13, validators=[uz_phone_validator])
    status = models.CharField(
        "Holat", max_length=20, choices=LeadStatus.choices, default=LeadStatus.NEW
    )
    manager_note = models.TextField("Menejer izohi", blank=True)
    created_at = models.DateTimeField("Yuborilgan", auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class TestDriveRequest(BaseLead):
    class TimeSlot(models.TextChoices):
        MORNING = "morning", "Ertalab (09:00–12:00)"
        AFTERNOON = "afternoon", "Kunduzi (12:00–16:00)"
        EVENING = "evening", "Kechqurun (16:00–20:00)"

    car = models.ForeignKey(
        "cars.Car", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="test_drives", verbose_name="Avtomobil",
    )
    preferred_date = models.DateField("Qulay sana")
    time_slot = models.CharField(
        "Vaqt", max_length=20, choices=TimeSlot.choices, default=TimeSlot.AFTERNOON
    )
    comment = models.TextField("Izoh", blank=True)

    class Meta(BaseLead.Meta):
        verbose_name = "Test-drayv arizasi"
        verbose_name_plural = "Test-drayv arizalari"

    def __str__(self) -> str:
        return f"{self.full_name} — {self.car or 'model tanlanmagan'} ({self.preferred_date})"


class ContactRequest(BaseLead):
    class Topic(models.TextChoices):
        CONSULTATION = "consultation", "Konsultatsiya"
        CREDIT = "credit", "Kredit / bo'lib to'lash"
        TRADE_IN = "trade_in", "Trade-in"
        SERVICE = "service", "Servis xizmati"

    topic = models.CharField(
        "Mavzu", max_length=20, choices=Topic.choices, default=Topic.CONSULTATION
    )
    car = models.ForeignKey(
        "cars.Car", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="contact_requests", verbose_name="Avtomobil",
    )
    message = models.TextField("Xabar", blank=True)

    class Meta(BaseLead.Meta):
        verbose_name = "Murojaat"
        verbose_name_plural = "Murojaatlar"

    def __str__(self) -> str:
        return f"{self.full_name} — {self.get_topic_display()}"
