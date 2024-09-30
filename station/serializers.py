from rest_framework import serializers
from station.models import Bus, Order, Trip


class BusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bus
        fields = ("id", "info", "num_seats")
        read_only_fields = ("id",)


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"


class TripSerializer(serializers.ModelSerializer):

    class Meta:
        model = Trip
        fields = "__all__"


class TripListSerializer(TripSerializer):
    bus = BusSerializer()
