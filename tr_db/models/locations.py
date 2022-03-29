from importlib.resources import _
from .base_models import BaseModel
from django.db import models


# TODO: add fields- country, region (perhaps enrich with maps api)
# TODO: consider removing routes update time
class Location(BaseModel):
    place_id = models.CharField(max_length=255, null=True)
    lng = models.FloatField(null=False)
    lat = models.FloatField(null=False)
    country = models.CharField(null=False, max_length=2)
    routes_update_time = models.DateTimeField(default=None, null=True)

    def __str__(self):
        return self.place_id


# TODO: add activity, theme (specific activity like harry potter)
# TODO: add places to work
# TODO: extend dates to a series of dates and seasons
class Interest(BaseModel):
    class Aspect(models.TextChoices):
        SKI = 'SKI', _('Ski')
        HIKING = 'HIKING', _('Hiking')
        BEACH = 'BEACH', _('Beach')
        MUSEUM = 'MUSEUM', _('Museum')
        PARTY = 'PARTY', _('Party')
        AMUSEMENT_PARK = 'AMUSEMENT_PARK', _('Amusement_park')
        CITY = 'CITY', _('City')
        CULINARY = 'CULINARY', _('Culinary')
        LOCAL_CULTURE = 'LOCAL_CULTURE', _('Local_culture')
        NIGHT_LIFE = 'NIGHT_LIFE', _('Night_life')

    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=False, related_name='interests')
    aspect = models.CharField(max_length=255, choices=Aspect.choices, null=False)
    start_date = models.DateField(null=False)
    end_date = models.DateField(null=False)


