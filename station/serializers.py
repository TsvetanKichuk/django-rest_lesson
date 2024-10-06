from django.db import transaction
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from station.models import Bus, Order, Trip, Facility, Ticket


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("id", "seat", "trip")

    def validate(self, attrs):
        Ticket.validate_seat(
            attrs["seat"],
            attrs["trip"].trip.bus.num_seats,
            serializers.ValidationError
        )


class FacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Facility
        fields = "__all__"


class BusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bus
        fields = ("id", "info", "num_seats", "facility")
        read_only_fields = ("id",)


class BusRetrieveSerializer(BusSerializer):
    facility = FacilitySerializer(many=True)  # детальное отображение автобуса


class BusListSerializer(BusSerializer):
    facility = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="name"
    )  # отображение поля facility


class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = "__all__"


class TripListSerializer(serializers.ModelSerializer):
    bus_info = serializers.CharField(source="bus.info", read_only=True)
    bus_num_seats = serializers.IntegerField(source="bus.num_seats", read_only=True)
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Trip
        fields = (
            "id",
            "source",
            "destination",
            "departure",
            "bus_info",
            "bus_num_seats",
            "tickets_available"
        )


class TripRetrieveSerializer(TripSerializer):
    bus = BusRetrieveSerializer(many=False, read_only=True)
    ticket = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="seat",
        source="tickets"
    )

    class Meta:
        model = Trip
        fields = ("id", "source", "destination", "departure", "bus", "ticket")


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "created_at", "tickets")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order


class TicketListSerializer(TicketSerializer):
    trip = TripListSerializer(read_only=True)


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(read_only=True, many=True)
