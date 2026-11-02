from rest_framework import generics, viewsets
from rest_framework.throttling import ScopedRateThrottle

from apps.cars.models import BodyType, Car

from .serializers import (
    BodyTypeSerializer,
    CarDetailSerializer,
    CarListSerializer,
    TestDriveRequestSerializer,
)


class BodyTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BodyType.objects.all()
    serializer_class = BodyTypeSerializer
    pagination_class = None


class CarViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Avtomobillar katalogi.

    Filtrlar: `?body=sedan&powertrain=ev&price_min=20000&price_max=40000&q=seal`
    """

    lookup_field = "slug"

    def get_queryset(self):
        qs = Car.objects.available().select_related("body_type")
        if self.action == "retrieve":
            return qs.prefetch_related("colors", "images")
        return qs.filter_by_params(self.request.query_params)

    def get_serializer_class(self):
        return CarDetailSerializer if self.action == "retrieve" else CarListSerializer


class TestDriveCreateView(generics.CreateAPIView):
    serializer_class = TestDriveRequestSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "leads"
