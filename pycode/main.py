import django

django.setup()
from trippin import tr_db
import datetime


# insert place to db with hard coded attributes ?
# manually insert places and aspects
# manually insert aspect to each location
# calculate a rout
def main():

    athens = tr_db.Location(place_id='ChIJ8UNwBh-9oRQR3Y1mdkU1Nic', lng=23.7275388, lat=37.9838096, country='GR', name='Athens')
    athens.save()

    agios_ioannis = tr_db.Location(place_id='ChIJDcrIHKQPpxQRgkoh91DnINA', lng=23.1609304, lat=39.4167434, country='GR', name='Agios Ioannis')
    agios_ioannis.save()

    litochoro = tr_db.Location(place_id='ChIJpZgb894OWBMR-ui9w_SD-oo', lng=22.5026117, lat=40.1029473, country='GR', name='Litochoro')
    litochoro.save()

    zagorochoria = tr_db.Location(place_id='ChIJBXfS0xy4WxMRjXxw7RNOEfc', lng=20.8552919, lat=39.8799973, country='GR',name='Zaguri')
    zagorochoria.save()

    athens_aspect_0 = tr_db.Interest(location_id=tr_db.Location.objects.filter(name='Athens').first().id, aspect=tr_db.Interest.Aspect.LOCAL_CULTURE,
                                     start_date=datetime.datetime(2020, 1, 1), end_date=datetime.datetime(2020, 12, 31))

    athens_aspect_0.save()

if __name__ == '__main__':
    main()


# class Interest(BaseModel):
#     class Aspect(models.TextChoices):
#         SKI = 'SKI', _('Ski')
#         HIKING = 'HIKING', _('Hiking')
#         BEACH = 'BEACH', _('Beach')
#         MUSEUM = 'MUSEUM', _('Museum')
#         PARTY = 'PARTY', _('Party')
#         AMUSEMENT_PARK = 'AMUSEMENT_PARK', _('Amusement_park')
#         CITY = 'CITY', _('City')
#         CULINARY = 'CULINARY', _('Culinary')
#         LOCAL_CULTURE = 'LOCAL_CULTURE', _('Local_culture')
#         NIGHT_LIFE = 'NIGHT_LIFE', _('Night_life')
#
#     location = models.ForeignKey(Location, on_delete=models.CASCADE, null=False)
#     aspect = models.CharField(max_length=255, choices=Aspect.choices, null=False)
#     start_date = models.DateField(null=False)
#     end_date = models.DateField(null=False)