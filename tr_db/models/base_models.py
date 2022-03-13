from django.db import models


class BaseModel(models.Model):
    name = models.CharField(max_length=255, null=True)

    class Meta:
        abstract = True
