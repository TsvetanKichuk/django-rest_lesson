from rest_framework import viewsets

from station.models import Bus, Trip
from station.serializers import (
    BusSerializer,
    TripSerializer,
    TripListSerializer,
    BusListSerializer,
)


class BusViewSet(viewsets.ModelViewSet):
    queryset = Bus.objects.all()
    serializer_class = BusListSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return BusListSerializer
        return BusSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action == "list":
            return queryset.prefetch_related("facility")

        return queryset


class TripViewSet(viewsets.ModelViewSet):
    queryset = Trip.objects.all().select_related("bus")

    def get_serializer_class(self):
        if self.action == "list":
            return TripListSerializer
        return TripSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action == "list":
            return queryset.select_related("bus")

        return queryset
