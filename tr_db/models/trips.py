from .base_models import BaseModel
from django.db import models
from .locations import Location
from .routes import Route


# TODO : convert to date range
# TODO :what else?
class Trip(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()


# TODO: convert to date range
# TODO: add cost
# TODO: car?
class TripSegment(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=False, related_name='trip_segments')
    next_segment = models.ForeignKey('TripSegment', on_delete=models.CASCADE, null=False, related_name='next_segment')
    contribution_by_aspect = models.FloatField(default=0)
    route = models.ForeignKey(Route, on_delete=models.CASCADE, null=False,
                              related_name='trip_segments')  # from this trips segment location to next? (TBD)
    start_date = models.DateField()
    end_date = models.DateField()  # exclusive
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, null=False, related_name='segments')
