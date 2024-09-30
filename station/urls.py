from django.urls import path, include
from station.views import BusViewSet, TripViewSet, FacilityViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register("buses", BusViewSet)
router.register("trips", TripViewSet)
router.register("facilities", FacilityViewSet)

urlpatterns = [
    path("", include(router.urls))
    ]

app_name = 'station'
