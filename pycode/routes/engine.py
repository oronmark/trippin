from typing import List, Optional
import amadeus
import googlemaps
from amadeus import Client, ResponseError
import os
import django
import logging

logging.basicConfig(level=logging.INFO)
django.setup()

from trippin import tr_db
from trippin.tr_db import Location, Route, Transportation, Airport, AirportConnection, FlightRoute, AirportLocation, \
    DriveRoute
from pycode.airports.airports import AirportsDAO
from django.db import transaction
from pycode.tr_utils import Coordinates, calculate_flight_time, calculate_distance_on_map


# TODO: add error handling, logging and costume exceptions
# TODO: remove optional
# TODO: build route for flight and check if mid routes will work
# TODO: unify all transactions to a single function
# TODO: add tracking bar
# TODO: consider using distance matrix rather the direction
# TODO: add transit type
# TODO: add legs count to route type
# TODO: airport connections is not efficient, refactor
# TODO: currently drive only and only first result, need to expand
# TODO: to start, make another call to google api for arrival from location to airport, instead of using existing routes
# TODO: remove airports dao from init, should be a singleton accessible to engine
class RoutesEngine:

    def __init__(self, gmaps_client: googlemaps.Client, airports_dao: AirportsDAO):
        self.gmaps_client = gmaps_client
        self.airports_dao = airports_dao

    def create_routes_amadeus(self) -> List[Transportation]:
        pass

    # TODO: rename
    def create_transportations(self, p0: Coordinates, p1: Coordinates, transportation_type: Transportation.Type) -> \
            List[Transportation]:

        transportations = []
        directions_result = self.gmaps_client.directions((p0.lat, p0.lng),
                                                         (p1.lat, p1.lng),
                                                         mode=transportation_type.get_string_value())

        for d in directions_result:
            result = d['legs'][0]
            transportations.append(tr_db.Transportation(distance=result['distance']['value'],
                                                        duration=result['duration']['value'],
                                                        legs=1))
        return transportations

    def create_transportations_by_route(self, route: Route, transportation_type: Transportation.Type) \
            -> List[Transportation]:
        return self.create_transportations(p0=Coordinates(lat=route.location_0.lat, lng=route.location_0.lng),
                                           p1=Coordinates(lat=route.location_1.lat, lng=route.location_1.lng),
                                           transportation_type=transportation_type)

    # TODO: add constraints to enable only viable routes (remove very long distance etc)
    def create_route_option_driving(self, route: Route) -> List[DriveRoute]:
        transportations = self.create_transportations_by_route(route, Transportation.Type.DRIVING)
        return [DriveRoute(route=route, transportation=t) for t in transportations]

    def create_route_option_transit(self, route: Route) -> List[Transportation]:
        pass

    # TODO: implement
    def create_routes_options(self, route: Route) -> List[Transportation]:
        pass

    # TODO: add transit to means of transportation
    def create_airport_location(self, airport: Airport, location: Location) -> List[AirportLocation]:
        transportations = self.create_transportations(
            p0=Coordinates(lat=airport.latitude_deg, lng=airport.longitude_deg),
            p1=Coordinates(lat=location.lat, lng=location.lng),
            transportation_type=Transportation.Type.DRIVING)

        return [AirportLocation(airport=airport, location=location, airport_transportation=t)
                for t in transportations]

    # TODO: find another way to couple location_0 with airport_0 etc
    # TODO: to start, use a single option of connected airports
    # TODO: to start use a single option for AirportLocation
    def create_route_option_flight(self, route: Route) -> FlightRoute:
        connected_airports = self.airports_dao.get_connected_airports_for_locations(route.location_0, route.location_1)
        if not connected_airports:
            raise Exception(f'Could not find any connected airports for route {route}')

        connection = connected_airports[0]
        airport_location_options_0 = self.create_airport_location(airport=connection.airport_0, location=route.location_0)
        airport_location_options_1 = self.create_airport_location(airport=connection.airport_1, location=route.location_1)

        if not airport_location_options_0:
            raise Exception(f'Could not find any transportation option from airport {connection.airport_0} '
                            f'location: {route.location_0}')

        if not airport_location_options_1:
            raise Exception(f'Could not find any transportation option from airport {connection.airport_1} '
                            f'location: {route.location_1}')

        return FlightRoute(airport_location_0=airport_location_options_0[0],
                           airport_location_1=airport_location_options_1[0])

    # # TODO: fix
    # def create_routes(self, new_location: Location) -> (List[Route], List[Transportation]):
    #
    #     routes = []
    #     route_types = []
    #     for location in Location.objects.all():
    #         new_route = tr_db.Route(location_0=new_location, location_1=location)
    #         routes.append(new_route)
    #         route_types.append(self.create_route_option_driving(new_route))
    #         # route_types.append(self.create_route_option_transit(new_route))
    #
    #     return routes, route_types


def main():
    airport_codes_subset_for_test = ['TLV', 'JFK', 'EWR', 'LAS', 'ATH', 'SKG']
    # airport_codes_subset_for_test = ['TLV']
    amadeus = Client(
        client_id=os.environ['AMADEUS_API_KEY'],
        client_secret=os.environ['AMADEUS_API_SECRET'],
        hostname='test'
    )
    gmaps = googlemaps.Client(key=os.environ['API_KEY'])
    # airports_dao = AirportsDAO(amadeus_client=amadeus)
    # routes_engine = RoutesEngine(gmaps_client=gmaps, airports_dao=airports_dao)
    #
    # # attempt to add airports routes for test airports
    # for code in airport_codes_subset_for_test:
    #     airport = tr_db.Airport.objects.filter(iata_code=code).get()
    #     airports_dao.create_airport_connections(airport)

    print('done')


if __name__ == '__main__':
    main()
