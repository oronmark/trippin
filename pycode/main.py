# THIS IS A SANDBOX

from typing import List

import django
from amadeus import Client
from pycode.airports.airports import AirportsDAO

django.setup()
from trippin import tr_db
from trippin.pycode import tr_utils
from routes.engine import RoutesEngine
import os
import googlemaps
from django.db.models import Q
from functools import reduce


###########################################################################################
###################################### GENERAL NOTES ######################################
###########################################################################################

# next session:
# save gmaps results and use without making an http call (for dev only)
# add maximal distance to craete drive route for

# open questions:
# how can I associate a city with an airport i.e tel aviv->ben gurion airport, new york city-> jfk and newark
# how can i mark a location as a reasonable place to reach an airport from
# removed duplicated iata_code from airports csv. should it be enough or should the key be id (for future files)
# how should models of pairs of same model should be handled to avoid repetition?

# TODOS:
# use distance matrix to eliminate places where you cant go by road
# check avg travel time with transit and driving
# change lng and lat for location to something more general (perhaps 3 coordinates with which represent borders)
# include fairies in driving and transit calculations (i.e athens to lesbos)
# make custome logger
# check how to do proper reverse lookup for generic relation
# try delete model
# run airport connection for all (or most) airports
# generalize symmetric filters for location, flight route etc

# misc:
# if there are no waypoints in the directions request there will be only 1 leg in the route

###########################################################################################
###########################################################################################
###########################################################################################

def create_locations():
    thessaloniki = tr_db.Location(place_id='ChIJ7eAoFPQ4qBQRqXTVuBXnugk', lng=22.9900712, lat=40.6560448, country='GR',
                                  name='Thessaloniki')
    tel_aviv = tr_db.Location(place_id='ChIJH3w7GaZMHRURkD-WwKJy-8E', lng=34.78176759999999, lat=32.0852999,
                              country='IL',
                              name='Tel-aviv')
    athens = tr_db.Location(place_id='ChIJ8UNwBh-9oRQR3Y1mdkU1Nic', lng=23.7275388, lat=37.9838096, country='GR',
                            name='Athens')
    agios_ioannis = tr_db.Location(place_id='ChIJDcrIHKQPpxQRgkoh91DnINA', lng=23.1609304, lat=39.4167434, country='GR',
                                   name='Agios Ioannis')
    litochoro = tr_db.Location(place_id='ChIJpZgb894OWBMR-ui9w_SD-oo', lng=22.5026117, lat=40.1029473, country='GR',
                               name='Litochoro')
    zagorochoria = tr_db.Location(place_id='ChIJBXfS0xy4WxMRjXxw7RNOEfc', lng=20.8552919, lat=39.8799973, country='GR',
                                  name='Zaguri')
    new_york = tr_db.Location(place_id='ChIJOwg_06VPwokRYv534QaPC8g', lng=-74.0059728, lat=40.7127753, country='US',
                              name='New York')
    eilat = tr_db.Location(place_id='ChIJC155JONxABUR2_Z3VfiVHf4', lng=35.0087689, lat=29.7630079,
                              country='IL',
                              name='Eilat')
    thessaloniki.save()
    tel_aviv.save()
    athens.save()
    agios_ioannis.save()
    litochoro.save()
    zagorochoria.save()
    new_york.save()
    eilat.save()


def create_manual_airport_connection(code_0: str, code_1: str):
    ap_0 = tr_db.Airport.objects.filter(iata_code=code_0).get()
    ap_1 = tr_db.Airport.objects.filter(iata_code=code_1).get()
    distance, travel_time = tr_utils.calculate_flight_stats(ap_0, ap_1)
    connection = tr_db.AirportsConnection(airport_0=ap_0, airport_1=ap_1, distance=distance, duration=travel_time,
                                          legs=1)
    connection.save()


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


def delete_db():
    tr_db.Transportation.objects.all().delete()
    tr_db.AirportLocation.objects.all().delete()
    tr_db.FlightRoute.objects.all().delete()
    tr_db.DriveRoute.objects.all().delete()
    tr_db.Route.objects.all().delete()
    tr_db.RouteOption.objects.all().delete()


# TODO: change input to flight route and not airport location
def create_airport_location_query(airport_locations: List[tr_db.AirportLocation]):
    airport_location_queries = [Q(airport_id=al.airport_id, location_id=al.location_id) for al in airport_locations]
    return reduce(lambda alq0, alq1: alq0 | alq1, airport_location_queries)


def main():
    # populate_airports_db()
    # create_locations()
    # create_airport_connections(['TLV', 'JFK', 'EWR', 'LAS', 'ATH', 'SKG'])
    # delete_db()
    # create_manual_airport_connection('TLV', 'ETM')

    gmaps = googlemaps.Client(key=os.environ['API_KEY'])
    amadeus = Client(
        client_id=os.environ['AMADEUS_API_KEY'],
        client_secret=os.environ['AMADEUS_API_SECRET'],
        hostname='test'
    )
    airports_dao = AirportsDAO(amadeus_client=amadeus)
    routes_engine = RoutesEngine(gmaps_client=gmaps, airports_dao=airports_dao)

    # tel_aviv = tr_db.Location.objects.filter(name='Tel-aviv').get()
    # new_york = tr_db.Location.objects.filter(name='New York').get()
    # athens = tr_db.Location.objects.filter(name='Athens').get()
    # agios_ionnis = tr_db.Location.objects.filter(name='Agios Ioannis').get()
    # eilat = tr_db.Location.objects.filter(name='Eilat').get()
    #
    # # route, route_options = routes_engine.create_route(athens, agios_ionnis)
    # # route, route_options = routes_engine.create_route(tel_aviv, new_york)
    # # routes_engine.save_route(route, route_options)
    #
    # # TODO: check why ramon airpot is not part of the answers
    # route, route_options = routes_engine.create_route(tel_aviv, eilat)
    # routes_engine.save_route(route, route_options)

    routes = routes_engine.run_engine()
    print('done')


if __name__ == '__main__':
    main()


