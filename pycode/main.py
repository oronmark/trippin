from typing import List

import django

django.setup()
from trippin import tr_db
from trippin.tr_db import Location, Route
import datetime


# # assumption, this location has no routs at all
# def create_location_routs(location: Location) -> List[Route]:


# insert place to db with hard coded attributes ?
# manually insert places and aspects
# manually insert aspect to each location
# calculate a rout
# use directions for how to get from point a to point b
# use distance matrix to eliminate places where you cant go by road
# check avg travel time with transit and driving
def main():
    import googlemaps
    from datetime import datetime
    import os

    gmaps = googlemaps.Client(key=os.environ['API_KEY'])

    # Geocoding an address
    # directions_result = gmaps.directions('37.9838096, 23.7275388', '40.6400629, 22.9444191', mode='driving')
    directions_result = gmaps.directions('afula', 'new york', mode='transit')
    print('done')

    # athens = tr_db.Location(place_id='ChIJ8UNwBh-9oRQR3Y1mdkU1Nic', lng=23.7275388, lat=37.9838096, country='GR', name='Athens')
    # athens.save()

    # agios_ioannis = tr_db.Location(place_id='ChIJDcrIHKQPpxQRgkoh91DnINA', lng=23.1609304, lat=39.4167434, country='GR', name='Agios Ioannis')
    # agios_ioannis.save()

    # litochoro = tr_db.Location(place_id='ChIJpZgb894OWBMR-ui9w_SD-oo', lng=22.5026117, lat=40.1029473, country='GR', name='Litochoro')
    # litochoro.save()
    #
    # zagorochoria = tr_db.Location(place_id='ChIJBXfS0xy4WxMRjXxw7RNOEfc', lng=20.8552919, lat=39.8799973, country='GR',name='Zaguri')
    # zagorochoria.save()
    #
    # athens_aspect_0 = tr_db.Interest(location_id=tr_db.Location.objects.filter(name='Athens').first().id, aspect=tr_db.Interest.Aspect.LOCAL_CULTURE,
    #                                  start_date=datetime.datetime(2020, 1, 1), end_date=datetime.datetime(2020, 12, 31))
    #
    # athens_aspect_0.save()


if __name__ == '__main__':
    main()
