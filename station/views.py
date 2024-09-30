from rest_framework import viewsets

from station.models import Bus, Trip, Facility
from station.serializers import (
    BusSerializer,
    TripSerializer,
    TripListSerializer,
    BusListSerializer,
    FacilitySerializer,
    BusRetrieveSerializer,
    TripRetrieveSerializer,
)


class FacilityViewSet(viewsets.ModelViewSet):
    queryset = Facility.objects.all()
    serializer_class = FacilitySerializer


class BusViewSet(viewsets.ModelViewSet):
    queryset = Bus.objects.all()
    serializer_class = BusListSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return BusListSerializer
        elif self.action == "retrieve":
            return BusRetrieveSerializer  # оптимизация отображения
        return BusSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action in ("list", "retrieve"):
            return queryset.prefetch_related("facility")   # оптимизация кверисетов

        return queryset


class TripViewSet(viewsets.ModelViewSet):
    queryset = Trip.objects.all().select_related("bus")

    def get_serializer_class(self):
        if self.action == "list":
            return TripListSerializer
        elif self.action == "retrieve":
            return TripRetrieveSerializer
        return TripSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action in ("list", "retrieve"):
            return queryset.select_related("bus")

        return queryset
