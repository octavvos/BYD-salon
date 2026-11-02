from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .models import Car


class CatalogTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_cars", stdout=StringIO())

    def test_seed_is_idempotent(self):
        call_command("seed_cars", stdout=StringIO())
        self.assertEqual(Car.objects.count(), 8)

    def test_pages_render(self):
        car = Car.objects.get(slug="byd-seal")
        for url in [reverse("home"), reverse("about"), reverse("cars:list"), car.get_absolute_url()]:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_filter_by_powertrain_and_body(self):
        response = self.client.get(reverse("cars:list"), {"powertrain": "dmi"})
        names = {c.name for c in response.context["cars"]}
        self.assertEqual(names, {"BYD Chazor", "BYD Song Plus DM-i"})

        response = self.client.get(reverse("cars:list"), {"body": "sedan", "powertrain": "ev"})
        self.assertEqual({c.name for c in response.context["cars"]}, {"BYD Seal", "BYD Han"})

    def test_price_filter_ignores_garbage(self):
        response = self.client.get(reverse("cars:list"), {"price_max": "abc"})
        self.assertEqual(response.context["paginator"].count, 8)

        response = self.client.get(reverse("cars:list"), {"price_max": "25000"})
        self.assertTrue(all(c.price <= 25000 for c in response.context["cars"]))

    def test_sort_by_price_desc(self):
        response = self.client.get(reverse("cars:list"), {"sort": "-price"})
        prices = [c.price for c in response.context["cars"]]
        self.assertEqual(prices, sorted(prices, reverse=True))

    def test_unavailable_car_is_hidden(self):
        car = Car.objects.get(slug="byd-tang")
        car.is_available = False
        car.save()
        self.assertEqual(self.client.get(car.get_absolute_url()).status_code, 404)
        self.assertNotIn(car, self.client.get(reverse("cars:list")).context["cars"])

    def test_discount_percent(self):
        car = Car.objects.get(slug="byd-seagull")
        self.assertEqual(car.discount_percent, 10)
        self.assertIsNone(Car.objects.get(slug="byd-seal").discount_percent)


class ApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_cars", stdout=StringIO())

    def test_car_list_and_filters(self):
        response = self.client.get("/api/cars/", {"powertrain": "ev", "body": "hatchback"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual({c["slug"] for c in response.json()["results"]}, {"byd-seagull", "byd-dolphin"})

    def test_car_detail_includes_specs_and_colors(self):
        data = self.client.get("/api/cars/byd-seal/").json()
        self.assertEqual(data["body_type"]["slug"], "sedan")
        self.assertEqual(data["power_hp"], 530)
        self.assertTrue(data["colors"])
