from django.db.models import Count, F

from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.pagination import PageNumberPagination

from permissions import IsAdminOrIfAuthenticatedReadOnly

from station.models import Bus, Trip, Facility, Order
from station.serializers import (
    BusSerializer,
    TripSerializer,
    TripListSerializer,
    BusListSerializer,
    FacilitySerializer,
    BusRetrieveSerializer,
    TripRetrieveSerializer,
    OrderSerializer,
    OrderListSerializer,
)


class FacilityViewSet(viewsets.ModelViewSet):
    queryset = Facility.objects.all()
    serializer_class = FacilitySerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class BusSetPagination(PageNumberPagination):
    page_size = 2
    page_size_query_param = 'page_size'
    max_page_size = 20


class BusViewSet(viewsets.ModelViewSet):
    queryset = Bus.objects.all()
    serializer_class = BusListSerializer
    pagination_class = BusSetPagination
    authentication_classes = [TokenAuthentication]
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    @staticmethod
    def _params_to_ins(query_string):
        return [int(str_id) for str_id in
                query_string.split(",")]  # функция фильтрации по id /station/buses/?facilities=1,2

    def get_serializer_class(self):
        if self.action == "list":
            return BusListSerializer
        elif self.action == "retrieve":
            return BusRetrieveSerializer  # оптимизация отображения
        return BusSerializer

    def get_queryset(self):
        queryset = self.queryset
        facilities = self.request.query_params.get("facilities")
        if facilities:
            facilities = self._params_to_ins(facilities)
            queryset = queryset.filter(facilities__id__in=facilities)
        if self.action in ("list", "retrieve"):
            return queryset.prefetch_related("facility")  # оптимизация кверисетов

        return queryset.distinct()


class TripViewSet(viewsets.ModelViewSet):
    queryset = Trip.objects.select_related("bus")

    def get_serializer_class(self):
        if self.action == "list":
            return TripListSerializer
        elif self.action == "retrieve":
            return TripRetrieveSerializer
        return TripSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action in "list":
            return queryset.select_related("bus").annotate(
                tickets_available=F("bus__num_seats") - Count("tickets")
                # функция оптимизации и подсчета оставшихся билетов
            )

        elif self.action in "retrieve":
            queryset.select_related("bus")

        return queryset


class OrderSetPagination(PageNumberPagination):
    page_size = 3
    page_size_query_param = 'page_size'
    max_page_size = 20


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    pagination_class = OrderSetPagination

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)
        if self.action in "list":
            queryset = queryset.prefetch_related("tickets__trip__bus")
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        serializer = self.serializer_class
        if self.action == "list":
            serializer = OrderListSerializer
        return serializer
