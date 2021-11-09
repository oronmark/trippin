from django.db import models
from django.utils.translation import gettext_lazy as _


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


# add activity, theme (specific activity like harry potter)
# add places to work
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

    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=False)
    aspect = models.CharField(max_length=255, choices=Aspect.choices, null=False)
    start_date = models.DateField(null=False)
    end_date = models.DateField(null=False)


class Route(BaseModel):
    from_location = models.ForeignKey(Location, on_delete=models.CASCADE, null=False)
    to_location = models.ForeignKey(Location, on_delete=models.CASCADE, null=False)
    car = models.FloatField()
    train = models.FloatField()
    bus = models.FloatField()
    walk = models.FloatField()

    class Meta:
        unique_together = ('from_location', 'to_location')
