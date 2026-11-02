from django.urls import path

from . import views

app_name = "cars"

urlpatterns = [
    path("", views.CarListView.as_view(), name="list"),
    path("<slug:slug>/", views.CarDetailView.as_view(), name="detail"),
]
