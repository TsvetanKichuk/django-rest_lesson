from rest_framework import serializers
from station.models import Bus, Order, Trip, Facility


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
    )   # отображение поля facility


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"


class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = "__all__"


class TripListSerializer(serializers.ModelSerializer):
    bus_info = serializers.CharField(source="bus.info", read_only=True)
    bus_num_seats = serializers.IntegerField(source="bus.num_seats", read_only=True)

    class Meta:
        model = Trip
        fields = ("id", "source", "destination", "departure", "bus_info", "bus_num_seats")


class TripRetrieveSerializer(TripSerializer):
    bus = BusRetrieveSerializer(many=False, read_only=True)  # детальное отображение автобуса
