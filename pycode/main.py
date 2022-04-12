# THIS IS A SANDBOX

from typing import List

import django
from amadeus import Client

from pycode.airports.airports import AirportsDAO

django.setup()
from trippin import tr_db
import datetime
from routes.engine import RoutesEngine
import os
import googlemaps


###########################################################################################
###################################### GENERAL NOTES ######################################
###########################################################################################

# next session:
# write routes to db
# add flight time to flight route
# add update time for locations - done
# run airport connection for all (or most) airports

# open questions:
# how can I associate a city with an airport i.e tel aviv->ben gurion airport, new york city-> jfk and newark
# how can i mark a location as a reasonable place to reach an airport from
# currently removed duplicated iata_code from airports csv. should it be enough or should the key be id

# TODOS:
# use distance matrix to eliminate places where you cant go by road
# check avg travel time with transit and driving
# change lng and lat for location to something more general (perhaps 3 coordinates with which represent borders)

# misc:
# if there are no waypoints in the directions request there will be only 1 leg in the route

###########################################################################################
###########################################################################################
###########################################################################################

def create_locations():
    thessaloniki = tr_db.Location(place_id='ChIJ7eAoFPQ4qBQRqXTVuBXnugk', lng=22.9900712, lat=40.6560448, country='GR',
                             name='Thessaloniki')
    tel_aviv = tr_db.Location(place_id='ChIJH3w7GaZMHRURkD-WwKJy-8E', lng=34.78176759999999, lat=32.0852999, country='IL',
                             name='Tel-aviv')
    athens = tr_db.Location(place_id='ChIJ8UNwBh-9oRQR3Y1mdkU1Nic', lng=23.7275388, lat=37.9838096, country='GR', name='Athens')
    agios_ioannis = tr_db.Location(place_id='ChIJDcrIHKQPpxQRgkoh91DnINA', lng=23.1609304, lat=39.4167434, country='GR', name='Agios Ioannis')
    litochoro = tr_db.Location(place_id='ChIJpZgb894OWBMR-ui9w_SD-oo', lng=22.5026117, lat=40.1029473, country='GR', name='Litochoro')
    zagorochoria = tr_db.Location(place_id='ChIJBXfS0xy4WxMRjXxw7RNOEfc', lng=20.8552919, lat=39.8799973, country='GR',name='Zaguri')
    new_york = tr_db.Location(place_id='ChIJOwg_06VPwokRYv534QaPC8g', lng=-74.0059728, lat=40.7127753, country='US',
                              name='New York')

    thessaloniki.save()
    tel_aviv.save()
    athens.save()
    agios_ioannis.save()
    litochoro.save()
    zagorochoria.save()
    new_york.save()


def create_airport_connections(codes: List[str]):
    amadeus = Client(
        client_id=os.environ['AMADEUS_API_KEY'],
        client_secret=os.environ['AMADEUS_API_SECRET'],
        hostname='test'
    )
    airports_dao = AirportsDAO(amadeus_client=amadeus)
    for code in codes:
        airport = tr_db.Airport.objects.filter(iata_code=code).get()
        airports_dao.create_airport_connections(airport)


def populate_airports_db():
    amadeus = Client(
        client_id=os.environ['AMADEUS_API_KEY'],
        client_secret=os.environ['AMADEUS_API_SECRET'],
        hostname='test'
    )
    airports_dao = AirportsDAO(amadeus_client=amadeus)
    airports_dao.dump_to_db()


def main():

    # populate_airports_db()
    # create_locations()
    # create_airport_connections(['TLV', 'JFK', 'EWR', 'LAS', 'ATH', 'SKG'])

    gmaps = googlemaps.Client(key=os.environ['API_KEY'])
    amadeus = Client(
        client_id=os.environ['AMADEUS_API_KEY'],
        client_secret=os.environ['AMADEUS_API_SECRET'],
        hostname='test'
    )
    airports_dao = AirportsDAO(amadeus_client=amadeus)
    routes_engine = RoutesEngine(gmaps_client=gmaps, airports_dao=airports_dao)

    tel_aviv = tr_db.Location.objects.filter(name='Tel-aviv').get()
    new_york = tr_db.Location.objects.filter(name='New York').get()
    route = tr_db.Route(location_0=tel_aviv, location_1=new_york)
    driving_route = routes_engine.create_route_option_driving(route)
    flight_route = routes_engine.create_route_option_flight(route)
    flight_route[0].save()

    print('done')


if __name__ == '__main__':
    main()
