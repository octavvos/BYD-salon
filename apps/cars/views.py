from django.db.models import Max, Min
from django.views.generic import DetailView, ListView

from apps.leads.forms import ContactForm, TestDriveForm

from .models import BodyType, Car

SORT_OPTIONS = {
    "price": ("Arzonroq", "price"),
    "-price": ("Qimmatroq", "-price"),
    "-range_km": ("Uzoqroq yuradi", "-range_km"),
    "acceleration": ("Tezroq", "acceleration"),
}


class CarListView(ListView):
    template_name = "cars/car_list.html"
    context_object_name = "cars"
    paginate_by = 9

    def get_queryset(self):
        qs = Car.objects.available().select_related("body_type").filter_by_params(self.request.GET)
        sort = self.request.GET.get("sort")
        if sort in SORT_OPTIONS:
            qs = qs.order_by(SORT_OPTIONS[sort][1])
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        params = self.request.GET.copy()
        params.pop("page", None)
        ctx.update(
            body_types=BodyType.objects.all(),
            powertrains=Car.Powertrain.choices,
            sort_options=[(key, label) for key, (label, _) in SORT_OPTIONS.items()],
            price_bounds=Car.objects.available().aggregate(lo=Min("price"), hi=Max("price")),
            current=self.request.GET,
            querystring=params.urlencode(),
            has_filters=any(params.get(k) for k in ("body", "powertrain", "q", "price_min", "price_max")),
        )
        return ctx


class CarDetailView(DetailView):
    template_name = "cars/car_detail.html"
    context_object_name = "car"

    def get_queryset(self):
        return (
            Car.objects.available()
            .select_related("body_type")
            .prefetch_related("colors", "images")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        car = self.object
        ctx["test_drive_form"] = TestDriveForm(initial={"car": car})
        ctx["credit_form"] = ContactForm(initial={"car": car, "topic": "credit"})
        ctx["similar"] = (
            Car.objects.available()
            .select_related("body_type")
            .filter(body_type=car.body_type)
            .exclude(pk=car.pk)[:3]
        )
        return ctx
