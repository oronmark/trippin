from .base_models import BaseModel
from django.db import models
from trippin.pycode.tr_utils import sort_attributes


class Airport(BaseModel):
    type = models.CharField(max_length=255, null=True)
    name = models.CharField(max_length=255, null=True)
    latitude_deg = models.FloatField(null=False)
    longitude_deg = models.FloatField(null=False)
    continent = models.CharField(max_length=2, null=True)
    iso_region = models.CharField(max_length=255, null=True)
    iso_country = models.CharField(max_length=2, null=True)
    municipality = models.CharField(max_length=255, null=True)
    gps_code = models.CharField(max_length=5, null=True)
    iata_code = models.CharField(max_length=3, null=True)
    connections_update_time = models.DateTimeField(default=None, null=True)
    metropolitan_iata_code = models.CharField(max_length=3, null=True)

    class Meta:
        unique_together = ['iata_code', 'id']

    def __str__(self):
        return self.iata_code


# TODO consider unifying with route model
class AirportsConnection(BaseModel):
    airport_0 = models.ForeignKey(Airport, on_delete=models.CASCADE, null=False, related_name='airport_0')
    airport_1 = models.ForeignKey(Airport, on_delete=models.CASCADE, null=False, related_name='airport_1')
    distance = models.IntegerField()
    travel_time = models.IntegerField()

    class Meta:
        unique_together = ('airport_0', 'airport_1')

    def save(self, *args, **kwargs):
        sort_attributes(self, lambda l: l.iata_code, ['airport_0', 'airport_1'])
        super(AirportsConnection, self).save(*args, **kwargs)
