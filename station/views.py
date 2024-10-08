from django.db.models import Count, F
from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

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
    OrderListSerializer, BusImageSerializer,
)


class FacilityViewSet(viewsets.ModelViewSet):
    queryset = Facility.objects.all()
    serializer_class = FacilitySerializer
    authentication_classes = [TokenAuthentication]

    # def get_permissions(self):
    #     if self.action in ('list', 'retrieve'):
    #         return (IsAuthenticated(),)
    #     return super().get_permissions()


class BusSetPagination(PageNumberPagination):
    page_size = 2
    page_size_query_param = 'page_size'
    max_page_size = 20


class BusViewSet(viewsets.ModelViewSet):
    queryset = Bus.objects.all()
    serializer_class = BusListSerializer
    pagination_class = BusSetPagination
    authentication_classes = [TokenAuthentication]
    @staticmethod
    def _params_to_ins(query_string):
        return [int(str_id) for str_id in
                query_string.split(",")]  # функция фильтрации по id /station/buses/?facilities=1,2

    def get_serializer_class(self):
        if self.action == "list":
            return BusListSerializer
        elif self.action == "retrieve":
            return BusRetrieveSerializer  # оптимизация отображения
        elif self.action == "upload_image":
            return BusImageSerializer
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

    @action(
        detail=True,
        methods=["POST"],
        url_path="upload-image",

    )
    def upload_image(self, request, pk=None):
        bus = self.get_object()
        serializer = self.get_serializer(bus, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
    authentication_classes = [TokenAuthentication]

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
