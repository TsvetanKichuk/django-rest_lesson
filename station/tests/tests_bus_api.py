from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from station.models import Bus, Facility
from station.serializers import BusListSerializer, BusSerializer, BusRetrieveSerializer

BUS_URL = reverse("station:bus-list")


def detail_url(bus_id):
    return reverse("station:bus-detail", args=(bus_id,))


def create_bus(**params):
    defaults = {
        "info": "AA 8889 OO",
        "num_seats": 50,
    }
    defaults.update(params)
    return Bus.objects.create(**defaults)


class UnauthenticatedBusApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(BUS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBusApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test",
            password="testpassword"
        )
        self.client.force_authenticate(self.user)

    def test_buses_list(self):
        create_bus()
        bus_with_facilities = create_bus()

        facility_1 = Facility.objects.create(name="WiFi")
        facility_2 = Facility.objects.create(name="TV")
        bus_with_facilities.facility.add(facility_1, facility_2)

        res = self.client.get(BUS_URL)
        buses = Bus.objects.all()
        serializer = BusListSerializer(buses, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_filter_buses_by_facilities(self):
        bus_without_facilities = create_bus()
        bus_with_facility_1 = create_bus(info="AA 8889 O1")
        bus_with_facility_2 = create_bus(info="AA 8889 O2")

        facility_1 = Facility.objects.create(name="WiFi")
        facility_2 = Facility.objects.create(name="TV")

        bus_with_facility_1.facility.add(facility_1)
        bus_with_facility_2.facility.add(facility_2)

        res = self.client.get(
            BUS_URL,
            {"facility": f"{facility_1.id},{facility_2.id}"}
        )

        serializer_without_facilities = BusListSerializer(bus_without_facilities)
        serializer_bus_facility_1 = BusListSerializer(bus_with_facility_1)
        serializer_bus_facility_2 = BusListSerializer(bus_with_facility_2)

        self.assertIn(serializer_bus_facility_1.data, res.data["results"])
        self.assertIn(serializer_bus_facility_2.data, res.data["results"])
        self.assertNotIn(serializer_without_facilities, res.data["results"])

    def test_retrieve_bus_details(self):
        bus = create_bus()
        bus.facility.add(Facility.objects.create(name="WiFi"))
        url = detail_url(bus.id)
        res = self.client.get(url)
        serializer = BusRetrieveSerializer(bus)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_bus_forbidden(self):
        payload = {
            "info": "AA 8889 O3",
            "num_seats": 50,
        }
        res = self.client.post(BUS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminBusTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admintest@test.test",
            password="testpassword",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)

    def test_create_bus(self):
        payload = {
            "info": "AA 8889 O3",
            "num_seats": 50,
        }
        res = self.client.post(BUS_URL, payload)
        bus = Bus.objects.get(id=res.data["id"])
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        for key in payload:
            self.assertEqual(payload[key], getattr(bus, key))

    def test_create_bus_with_facilities(self):
        facility_1 = Facility.objects.create(name="WiFi")
        facility_2 = Facility.objects.create(name="TV")
        payload = {
            "info": "AA 8889 O4",
            "num_seats": 50,
            "facility": [facility_1.id, facility_2.id]
        }

        res = self.client.post(BUS_URL, payload)
        bus = Bus.objects.get(id=res.data["id"])
        facilities = bus.facility.all()
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn(facility_1, facilities)
        self.assertIn(facility_2, facilities)
        self.assertEqual(facilities.count(), 2)

    def test_delete_bus_not_allowed(self):
        bus = create_bus()
        url = detail_url(bus.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
