from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View

from apps.cars.models import Car

from .forms import ContactForm, TestDriveForm


def _safe_next(request, fallback: str) -> str:
    target = request.POST.get("next") or request.GET.get("next")
    if target and url_has_allowed_host_and_scheme(
        target, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return target
    return fallback


class TestDriveView(View):
    template_name = "leads/test_drive.html"

    def get(self, request):
        initial = {}
        if slug := request.GET.get("car"):
            initial["car"] = Car.objects.available().filter(slug=slug).first()
        return render(request, self.template_name, {"form": TestDriveForm(initial=initial)})

    def post(self, request):
        form = TestDriveForm(request.POST)
        if form.is_valid():
            lead = form.save()
            messages.success(
                request,
                f"Rahmat, {lead.full_name}! Test-drayv arizangiz qabul qilindi — "
                "menejerimiz tez orada qo'ng'iroq qiladi.",
            )
            return redirect(_safe_next(request, "leads:test_drive"))
        return render(request, self.template_name, {"form": form}, status=400)


class ContactView(View):
    template_name = "leads/contacts.html"

    def get(self, request):
        topic = request.GET.get("topic", ContactForm.base_fields["topic"].initial)
        return render(request, self.template_name, {"form": ContactForm(initial={"topic": topic})})

    def post(self, request):
        form = ContactForm(request.POST)
        if form.is_valid():
            lead = form.save()
            messages.success(
                request,
                f"Rahmat, {lead.full_name}! Murojaatingiz qabul qilindi, tez orada bog'lanamiz.",
            )
            return redirect(_safe_next(request, "leads:contacts"))
        return render(request, self.template_name, {"form": form}, status=400)
