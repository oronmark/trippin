from typing import List

from .base_models import BaseModel
from django.db import models
from .locations import Location, GeneralLocation
from .airports import Airport
from trippin.pycode.tr_utils import sort_attributes
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


# TODO: what should a rout stand for ? the time it takes to get from  point a to point b? for poc yes
# TODO: add mixed transportation type (i.e driving and transit)
# TODO: fix nullable fields
class Route(BaseModel):
    location_0 = models.ForeignKey(Location, on_delete=models.CASCADE, null=False, related_name='location_0')
    location_1 = models.ForeignKey(Location, on_delete=models.CASCADE, null=False, related_name='location_1')

    class Meta:
        unique_together = [('location_0', 'location_1')]

    # sorting the attributes makes the unique_together constraint symmetrical
    def save(self, *args, **kwargs):
        sort_attributes(self, lambda l: l.place_id, ['location_0', 'location_1'])
        super(Route, self).save(*args, **kwargs)

    def __str__(self):
        return f'location_0={self.location_0.name}, location_1={self.location_1.name}'


class Transportation(BaseModel):
    class Type(models.TextChoices):
        DRIVING = 'driving',
        TRANSIT = 'transit',
        FLIGHT = 'flight'

        def get_string_value(self):
            return self.value[0]

    distance = models.IntegerField(null=True)
    duration = models.IntegerField(null=True)
    legs = models.IntegerField(null=True)
    type = models.CharField(max_length=255, choices=Type.choices, default=Type.DRIVING)


# TODO: add several options of airport arrival (transit, driving)
# TODO: rename
class AirportLocation(BaseModel):
    airport = models.ForeignKey(Airport, on_delete=models.CASCADE, null=False, related_name='airport')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=False, related_name='location')
    transportation = models.OneToOneField(Transportation, on_delete=models.CASCADE, null=False,
                                          related_name='transportation')

    class Meta:
        unique_together = [('airport', 'location')]

    def __str__(self):
        return f'airport={self.airport.iata_code}, location={self.location.name}'


class RouteOption(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, null=False, related_name='route_options')

    content_object = GenericForeignKey()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()


class BaseRoute(models.Model):
    transportation = models.OneToOneField(Transportation, on_delete=models.CASCADE, null=True,
                                          related_name='transportation', default=None)

    class Meta:
        abstract = True


# TODO: consider adding details regarding multi leg flights
# TODO: make nullable false
class FlightRoute(BaseRoute):
    airport_location_0 = models.ForeignKey(AirportLocation, on_delete=models.CASCADE,
                                           null=True, related_name='airport_location_0')
    airport_location_1 = models.ForeignKey(AirportLocation, on_delete=models.CASCADE,
                                           null=True, related_name='airport_location_1')

    class Meta:
        unique_together = [('airport_location_0', 'airport_location_1')]

    def save(self, *args, **kwargs):
        sort_attributes(self, lambda al: (al.airport.iata_code, al.location.place_id),
                        ['airport_location_0', 'airport_location_1'])
        super(FlightRoute, self).save(*args, **kwargs)

    def get_airport_locations(self) -> List[AirportLocation]:
        return [self.airport_location_0, self.airport_location_1]


class DriveRoute(BaseRoute):
    pass


class TransitRoute(BaseRoute):
    pass
