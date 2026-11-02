from django.views.generic import TemplateView

from apps.cars.models import BodyType, Car
from apps.leads.forms import TestDriveForm


class HomeView(TemplateView):
    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        featured = list(Car.objects.featured().select_related("body_type")[:6])
        ctx.update(
            # Hero'da eng kuchli model — vizual jihatdan eng ta'sirli
            hero_car=max(featured, key=lambda car: car.power_hp, default=None)
            or Car.objects.available().first(),
            featured=featured,
            body_types=BodyType.objects.all(),
            test_drive_form=TestDriveForm(),
        )
        return ctx


class AboutView(TemplateView):
    template_name = "core/about.html"
