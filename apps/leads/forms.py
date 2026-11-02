from datetime import timedelta

from django import forms
from django.utils import timezone

from apps.cars.models import Car

from .models import ContactRequest, TestDriveRequest, normalize_phone

TEST_DRIVE_MAX_DAYS = 60


def validate_test_drive_date(value):
    today = timezone.localdate()
    if value < today:
        raise forms.ValidationError("O'tgan sanani tanlab bo'lmaydi.")
    if value > today + timedelta(days=TEST_DRIVE_MAX_DAYS):
        raise forms.ValidationError(f"Yozilish {TEST_DRIVE_MAX_DAYS} kun oldinga ochiq.")


class LeadFormMixin(forms.Form):
    """Telefonni normallashtirish va spam botlar uchun ko'rinmas honeypot maydoni."""

    phone = forms.CharField(
        label="Telefon",
        max_length=32,
        widget=forms.TextInput(attrs={
            "placeholder": "+998 90 123 45 67", "inputmode": "tel",
            "autocomplete": "tel", "data-phone-mask": "",
        }),
    )
    website = forms.CharField(required=False, widget=forms.HiddenInput)

    def clean_phone(self):
        return normalize_phone(self.cleaned_data["phone"])

    def clean_website(self):
        if self.cleaned_data.get("website"):
            raise forms.ValidationError("Spam aniqlandi.")
        return ""


class TestDriveForm(LeadFormMixin, forms.ModelForm):
    class Meta:
        model = TestDriveRequest
        fields = ["car", "full_name", "phone", "preferred_date", "time_slot", "comment"]
        widgets = {
            "full_name": forms.TextInput(attrs={"placeholder": "Ismingiz", "autocomplete": "name"}),
            "preferred_date": forms.DateInput(attrs={"type": "date"}),
            "comment": forms.Textarea(attrs={"rows": 3, "placeholder": "Qo'shimcha istaklar (ixtiyoriy)"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["car"].queryset = Car.objects.available()
        self.fields["car"].empty_label = "Modelni tanlang"
        self.fields["car"].required = True
        today = timezone.localdate()
        self.fields["preferred_date"].widget.attrs.update(
            min=today.isoformat(), max=(today + timedelta(days=TEST_DRIVE_MAX_DAYS)).isoformat()
        )

    def clean_preferred_date(self):
        value = self.cleaned_data["preferred_date"]
        validate_test_drive_date(value)
        return value


class ContactForm(LeadFormMixin, forms.ModelForm):
    class Meta:
        model = ContactRequest
        fields = ["topic", "car", "full_name", "phone", "message"]
        widgets = {
            "car": forms.HiddenInput,
            "full_name": forms.TextInput(attrs={"placeholder": "Ismingiz", "autocomplete": "name"}),
            "message": forms.Textarea(attrs={"rows": 4, "placeholder": "Savolingiz yoki xabaringiz"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["car"].queryset = Car.objects.available()
