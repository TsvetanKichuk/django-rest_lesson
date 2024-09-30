from django.urls import path, include
from station.views import BusViewSet, TripViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register("buses", BusViewSet)
router.register("trips", TripViewSet)

urlpatterns = [
    path("", include(router.urls))
    ]

app_name = 'station'
