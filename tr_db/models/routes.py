from enum import Enum
from .base_models import BaseModel
from django.db import models
from .locations import Location
from .airports import Airport
from trippin.pycode.tr_utils import sort_attributes


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


    # def save(self, *args, **kwargs):
    #     if self.location_0.place_id > self.location_1.place_id:
    #         temp = self.location_0
    #         self.location_0 = self.location_1
    #         self.location_1 = temp
    #     super(Route, self).save(*args, **kwargs)

    def __str__(self):
        return f'location_0={self.location_0.name}, location_1={self.location_1.name}'


class Transportation(BaseModel):
    class Type(Enum):
        DRIVING = 'driving',
        TRANSIT = 'transit',
        FLIGHT = 'flight'

        def get_string_value(self):
            return self.value[0]

    distance = models.IntegerField(null=True)
    duration = models.IntegerField(null=True)
    legs = models.IntegerField(null=True)


# TODO: add several options of airport arrival (transit, driving)
# TODO: rename
class AirportLocation(BaseModel):
    airport = models.ForeignKey(Airport, on_delete=models.CASCADE, null=False,
                                related_name='airport')
    airport_transportation = models.OneToOneField(Transportation, on_delete=models.CASCADE, null=False,
                                                  related_name='airport_transportation')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=False, related_name='location')


class RouteOption(BaseModel):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, null=False, related_name='route_options')
    transportation = models.OneToOneField(Transportation, on_delete=models.CASCADE, null=True,
                                          related_name='transportation')

    class Meta:
        abstract = True


# TODO: consider adding details regarding multi leg flights
# TODO: make nullable false
class FlightRoute(RouteOption):
    airport_location_0 = models.OneToOneField(AirportLocation, on_delete=models.CASCADE,
                                              null=True, related_name='airport_location_0')
    airport_location_1 = models.OneToOneField(AirportLocation, on_delete=models.CASCADE,
                                              null=True, related_name='airport_location_1')

    class Meta:
        unique_together = [('airport_location_0', 'airport_location_1'), ('airport_location_1', 'airport_location_0')]


class DriveRoute(RouteOption):
    pass


class TransitRoute(RouteOption):
    pass
