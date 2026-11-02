from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "api"

router = DefaultRouter()
router.register("cars", views.CarViewSet, basename="car")
router.register("body-types", views.BodyTypeViewSet, basename="body-type")

urlpatterns = [
    path("", include(router.urls)),
    path("test-drive/", views.TestDriveCreateView.as_view(), name="test-drive"),
]
