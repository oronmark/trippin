from base_models import BaseModel
from django.db import models


class Airport(BaseModel):
    id = models.CharField(primary_key=True, max_length=255, null=True)
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


# TODO consider unifying with route model
class ConnectedAirports(BaseModel):
    airport_0 = models.ForeignKey(Airport, on_delete=models.CASCADE, null=False, related_name='airport_0')
    airport_1 = models.ForeignKey(Airport, on_delete=models.CASCADE, null=False, related_name='airport_1')

    class Meta:
        unique_together = ('airport_0', 'airport_1')
