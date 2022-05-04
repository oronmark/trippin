from datetime import date
from importlib.resources import _
from .base_models import BaseModel, Coordinates
from django.db import models


class GeneralLocation(BaseModel, Coordinates):
    def __str__(self):
        return self.name if self.name else Coordinates.__str__(self)

    class Meta:
        abstract = True


class UserLocation(GeneralLocation):
    pass


# TODO !!! expand general_location and remove str
# TODO: add fields- country, region (perhaps enrich with maps api)
# TODO: consider removing routes update time
class Location(GeneralLocation):
    place_id = models.CharField(max_length=255, null=True, unique=True)
    country = models.CharField(null=False, max_length=2)
    routes_update_time = models.DateTimeField(default=None, null=True)


# TODO: add activity, theme (specific activity like harry potter)
# TODO: add places to work, add more aspects
# TODO: extend dates to a series of dates and seasons
# TODO: currently dates are with year which is no used, consider changing
# TODO: if aspect does not exist it has 0 in the score field and is not relevant at all
# TODO: add option for cross location activities such as camino de santiago
class Interest(BaseModel):
    FIRST_DAY_OF_THE_YEAR = date(date.today().year, 1, 1)
    LAST_DAY_OF_THE_YEAR = date(date.today().year, 12, 31)

    class Aspect(models.TextChoices):
        SKI = 'SKI', _('Ski')
        HIKING = 'HIKING', _('Hiking')
        BEACH = 'BEACH', _('Beach')
        MUSEUM = 'MUSEUM', _('Museum')
        PARTY = 'PARTY', _('Party')
        AMUSEMENT_PARK = 'AMUSEMENT_PARK', _('Amusement_park')
        CITY = 'CITY', _('City')
        CULINARY = 'CULINARY', _('Culinary')
        LOCAL_CULINARY = 'LOCAL_CULINARY', _('Local_culinary')
        LOCAL_CULTURE = 'LOCAL_CULTURE', _('Local_culture')
        NIGHT_LIFE = 'NIGHT_LIFE', _('Night_life')
        PUBLIC_TRANSPORTATION = 'PUBLIC_TRANSPORTATION', _('Public_transportation')
        HISTORY = 'HISTORY', _('History')
        TREKKING = 'TREKKING', _('Trekking')
        RAFTING_CANYONING_RAPPELLING = 'RAFTING_CANYONING_RAPPELLING'

    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=False, related_name='interests')
    aspect = models.CharField(max_length=255, choices=Aspect.choices, null=False)
    score = models.FloatField(default=100)  # a score ranges in 0-100 for how strong this aspect is for this location
    start_date = models.DateField(null=False, default=FIRST_DAY_OF_THE_YEAR)
    end_date = models.DateField(null=False, default=LAST_DAY_OF_THE_YEAR)  # exclusive
