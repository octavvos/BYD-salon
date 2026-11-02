from datetime import timedelta
from io import StringIO

from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from apps.cars.models import Car

from .models import ContactRequest, TestDriveRequest, normalize_phone


class PhoneTests(TestCase):
    def test_normalize_phone(self):
        for raw in ["+998 (90) 123-45-67", "998901234567", "90 123 45 67"]:
            with self.subTest(raw=raw):
                self.assertEqual(normalize_phone(raw), "+998901234567")


class LeadFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_cars", stdout=StringIO())
        cls.car = Car.objects.get(slug="byd-seal")

    def payload(self, **overrides):
        data = {
            "car": self.car.pk,
            "full_name": "Aziz Karimov",
            "phone": "+998 90 123 45 67",
            "preferred_date": (timezone.localdate() + timedelta(days=2)).isoformat(),
            "time_slot": "evening",
        }
        data.update(overrides)
        return data

    def test_test_drive_created_and_redirects_to_next(self):
        response = self.client.post(
            reverse("leads:test_drive"), {**self.payload(), "next": self.car.get_absolute_url()}
        )
        self.assertRedirects(response, self.car.get_absolute_url())
        lead = TestDriveRequest.objects.get()
        self.assertEqual(lead.phone, "+998901234567")
        self.assertEqual(lead.car, self.car)

    def test_external_next_is_ignored(self):
        response = self.client.post(
            reverse("leads:test_drive"), {**self.payload(), "next": "https://evil.example/"}
        )
        self.assertRedirects(response, reverse("leads:test_drive"))

    def test_past_date_rejected(self):
        yesterday = (timezone.localdate() - timedelta(days=1)).isoformat()
        response = self.client.post(reverse("leads:test_drive"), self.payload(preferred_date=yesterday))
        self.assertEqual(response.status_code, 400)
        self.assertFalse(TestDriveRequest.objects.exists())

    def test_bad_phone_rejected(self):
        response = self.client.post(reverse("leads:test_drive"), self.payload(phone="12345"))
        self.assertEqual(response.status_code, 400)
        self.assertIn("phone", response.context["form"].errors)

    def test_honeypot_blocks_bots(self):
        response = self.client.post(reverse("leads:test_drive"), self.payload(website="spam.com"))
        self.assertEqual(response.status_code, 400)
        self.assertFalse(TestDriveRequest.objects.exists())

    def test_credit_request_from_car_page(self):
        response = self.client.post(reverse("leads:contacts"), {
            "topic": "credit", "car": self.car.pk, "full_name": "Dilnoza",
            "phone": "93 555 44 33", "message": "36 oy", "next": self.car.get_absolute_url(),
        })
        self.assertRedirects(response, self.car.get_absolute_url())
        lead = ContactRequest.objects.get()
        self.assertEqual((lead.topic, lead.phone), ("credit", "+998935554433"))

    @override_settings(TELEGRAM_BOT_TOKEN="", TELEGRAM_CHAT_ID="")
    def test_api_test_drive(self):
        response = self.client.post(
            "/api/test-drive/", {**self.payload(), "car": "byd-seal"}, content_type="application/json"
        )
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(TestDriveRequest.objects.get().phone, "+998901234567")

    def test_api_rejects_past_date(self):
        yesterday = (timezone.localdate() - timedelta(days=1)).isoformat()
        response = self.client.post(
            "/api/test-drive/", {**self.payload(preferred_date=yesterday), "car": "byd-seal"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("preferred_date", response.json())
