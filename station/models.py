from django.db import models
from django.db.models import UniqueConstraint

from django_rest_lesson import settings


class Facility(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = 'facilities'

    def __str__(self):
        return f"{self.name}"


class Bus(models.Model):
    info = models.CharField(max_length=255, null=True)
    num_seats = models.IntegerField()
    facility = models.ManyToManyField("Facility", related_name="buses")

    class Meta:
        verbose_name = "buses"

    @property
    def is_small(self):
        return self.num_seats <= 25

    def __str__(self):
        return f" Bus: {self.info} (id: {self.id})"


class Trip(models.Model):
    source = models.CharField(max_length=63)
    destination = models.CharField(max_length=255)
    departure = models.TimeField()
    bus = models.ForeignKey("Bus", on_delete=models.CASCADE, related_name="trips")

    class Meta:
        indexes = [
            models.Index(fields=["source", "destination"]),
            models.Index(fields=["departure"])
        ]

    def __str__(self):
        return f"{self.source}, {self.destination}, {self.departure}"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user}, {self.created_at}"


class Ticket(models.Model):
    seat = models.IntegerField()
    trip = models.ForeignKey("Trip", on_delete=models.CASCADE, related_name="tickets")
    order = models.ForeignKey("Order", on_delete=models.CASCADE, related_name="tickets")

    class Meta:
        constraints = [
            UniqueConstraint(fields=["seat", "trip"], name="unique_ticket_seat_trip")
        ]

    def __str__(self):
        return f"{self.trip} seat: {self.seat}"

    @staticmethod
    def validate_seat(seat, num_seat, error_to_raise):
        if not (1 <= seat <= num_seat):
            raise error_to_raise({
                "seat": f"seat must be in range [1 and {num_seat}], not {seat}"
            })

    def clean(self):
        Ticket.validate_seat(self.seat, self.trip.bus.num_seats, ValueError)
        # if not (1 <= self.seat <= self.trip.bus.num_seats):
        #     raise ValueError({
        #         "seat": f"seat must be in range[1, {self.trip.bus.num_seats}], not {self.seat}"
        #     })

    def save(
            self,
            force_insert=False,
            force_update=False,
            using=None,
            update_fields=None
    ):
        self.full_clean()
        return super(Ticket, self).save(force_insert, force_update, using, update_fields)
