from importlib.resources import _

from django.db import models


class BaseModel(models.Model):
    name = models.CharField(max_length=255, null=True)

    class Meta:
        abstract = True


# add fields- country, region (perhaps enrich with maps api)
class Location(BaseModel):
    place_id = models.CharField(max_length=255, null=True)
    lng = models.FloatField(null=False)
    lat = models.FloatField(null=False)
    country = models.CharField(null=False, max_length=2)

    # TODO: add unique key
    # class Meta:
    #     unique_together = 'place_id'


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


# TODO: consider converting to symetrical model (loc1, loc2 = loc2,loc1)
# TODO: what should a rout stand for ? the time it takes to get from  point a to point b? for poc yes
# TODO: add mixed transportation type (i.e driving and transit)
class Route(BaseModel):
    location_0 = models.ForeignKey(Location, on_delete=models.CASCADE, null=False, related_name='location_0')
    location_1 = models.ForeignKey(Location, on_delete=models.CASCADE, null=False, related_name='location_1')

    class Meta:
        unique_together = ('location_0', 'location_1')


class TransportationType(BaseModel):
    distance = models.IntegerField(null=True)
    duration = models.IntegerField(null=True)
    legs = models.IntegerField(null=True)
    route = models.ForeignKey(Route, on_delete=models.CASCADE, null=False, related_name='routes')

    class Meta:
        abstract = True


class DriveType(TransportationType):
    pass


# TODO: add type of transit (bus, boat etc)
class TransitType(TransportationType):
    pass


class FlightType(TransportationType):
    pass
