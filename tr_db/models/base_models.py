from django.db import models


class BaseModel(models.Model):
    name = models.CharField(max_length=255, null=True)

    class Meta:
        abstract = True


class Coordinates(models.Model):
    lat = models.FloatField()
    lng = models.FloatField()

    class Meta:
        abstract = True

    def __str__(self):
        return f'({self.lat},{self.lng})'
