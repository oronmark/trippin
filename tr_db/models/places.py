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

    # class Meta:
    #     unique_together = 'place_id'


# add activity, theme (specific activity like harry potter)
# add places to work
# extend dates to a series of dates
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


#consider converting to symetrical model (loc1, loc2 = loc2,loc1)
# not the actual rout , rather the possibility of traveling between 2 locations and in what ways
class Route(BaseModel):
    location_0 = models.ForeignKey(Location, on_delete=models.CASCADE, null=False, related_name='location_0')
    location_1 = models.ForeignKey(Location, on_delete=models.CASCADE, null=False, related_name='location_1')
    car = models.FloatField()
    train = models.FloatField()
    bus = models.FloatField()
    walk = models.FloatField()

    class Meta:
        unique_together = ('location_0', 'location_1')

