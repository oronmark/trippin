from enum import Enum
from .base_models import BaseModel
from django.db import models
from .locations import Location
from .airports import Airport


# TODO: consider converting to symmetrical model (loc1, loc2 = loc2,loc1) (check if meta is working)
# TODO: what should a rout stand for ? the time it takes to get from  point a to point b? for poc yes
# TODO: add mixed transportation type (i.e driving and transit)
# TODO: fix nullable fields
class Route(BaseModel):
    location_0 = models.ForeignKey(Location, on_delete=models.CASCADE, null=False, related_name='location_0')
    location_1 = models.ForeignKey(Location, on_delete=models.CASCADE, null=False, related_name='location_1')

    class Meta:
        unique_together = [('location_0', 'location_1'), ('location_1', 'location_0')]


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
class Flight(BaseModel):
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
class FlightRoute(RouteOption):
    flight_0 = models.OneToOneField(Flight, on_delete=models.CASCADE, null=False, related_name='flight_0')
    flight_1 = models.OneToOneField(Flight, on_delete=models.CASCADE, null=False, related_name='flight_1')

    class Meta:
        unique_together = [('flight_0', 'flight_1'), ('flight_1', 'flight_0')]


class DriveRoute(RouteOption):
    pass


class TransitRoute(RouteOption):
    pass
