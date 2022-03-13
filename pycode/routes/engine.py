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
from trippin.tr_db import Location, Route, Transportation, Airport, AirportConnection, FlightRoute, Flight, DriveRoute
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
class RoutesEngine:

    def __init__(self, gmaps_client: googlemaps.Client, airports_dao: AirportsDAO):
        self.gmaps_client = gmaps_client
        self.airports_dao = airports_dao

    def create_routes_amadeus(self) -> List[Transportation]:
        pass

    # TODO: rename
    def create_transportations(self, p0: Coordinates, p1: Coordinates, transportation_type: Transportation.Type) -> \
    List[
        Transportation]:

        transportations = []
        directions_result = self.gmaps_client.directions((p0.lat, p0.lng),
                                                         (p1.lat, p1.lng),
                                                         mode=transportation_type.get_string_value())

        if directions_result:
            first_result = directions_result[0]['legs'][0]
            drive_type = tr_db.Transportation(distance=first_result['distance']['value'],
                                              duration=first_result['duration']['value'],
                                              legs=1)
            transportations.append(drive_type)
        return transportations

    def create_transportations_by_route(self, route: Route, transportation_type: Transportation.Type) -> List[
        Transportation]:
        return self.create_transportations(p0=Coordinates(lat=route.location_0.lat, lng=route.location_0.lng),
                                           p1=Coordinates(lat=route.location_1.lat, lng=route.location_1.lng),
                                           transportation_type=transportation_type)

    def create_route_option_driving(self, route: Route) -> DriveRoute:
        return DriveRoute(route=route,
                          transportation=self.create_transportations_by_route(route, Transportation.Type.DRIVING))

    def create_route_option_transit(self, route: Route) -> List[Transportation]:
        pass

    # TODO: implement
    def create_routes_options(self, route: Route) -> List[Transportation]:
        pass

    def create_flight(self, airport: Airport, location: Location) -> Flight:
        airport_transportation = self.create_transportations(
            p0=Coordinates(lat=airport.latitude_deg, lng=airport.longitude_deg),
            p1=Coordinates(lat=location.lat, lng=location.lng),
            transportation_type=Transportation.Type.DRIVING)
        return Flight(airport=airport, location=location, airport_transportation=airport_transportation)

    # TODO: need refactor, this is all wrong!
    # TODO: add check if there is an airport connection to verify flight
    def create_route_option_flight(self, route: Route) -> FlightRoute:
        connected_airports
        # closest_airports_0 = self.airports_dao.get_closest_distances_by_airport(route.location_0,
        #                                                                         self.MAX_AIRPORT_DISTANCE)
        # closest_airports_1 = self.airports_dao.get_closest_distances_by_airport(route.location_1,
        #                                                                         self.MAX_AIRPORT_DISTANCE)
        # closest_airport_data_0 = min(closest_airports_0, key=lambda a: a.distance).airport_data
        # closest_airport_data_1 = min(closest_airports_1, key=lambda a: a.distance).airport_data
        # if not closest_airports_0 or not closest_airports_1:
        #     raise Exception('Could not find any airport close enough to location')
        #
        # # TODO: cannot guarantee order, fix this and check if db_airports were found
        # db_airports = self.airports_dao.get_airports_by_airport_data([closest_airport_data_0, closest_airport_data_1])
        #
        # if len(db_airports) < 2:
        #     raise Exception('Not all db airports were found')
        #
        # flight_0 = self.create_flight(airport=db_airports[0], location=route.location_0)
        # flight_1 = self.create_flight(airport=db_airports[1], location=route.location_1)
        # # distance = calculate_distance_on_map((db_airports[0].latitude_deg, db_airports[0].longitude_deg),
        # #                                      (db_airports[1].latitude_deg, db_airports[1].longitude_deg))
        # # duration = calculate_flight_time((db_airports[0].latitude_deg, db_airports[0].longitude_deg),
        # #                                      (db_airports[1].latitude_deg, db_airports[1].longitude_deg))
        # transportation = Transportation(duration=duration, distance=distance, legs=1)
        # return FlightRoute(flight_0=flight_0, flight_1=flight_1, route=route, transportation=transportation)


    # TODO: fix
    def create_routes(self, new_location: Location) -> (List[Route], List[Transportation]):

        routes = []
        route_types = []
        for location in Location.objects.all():
            new_route = tr_db.Route(location_0=new_location, location_1=location)
            routes.append(new_route)
            route_types.append(self.create_route_option_driving(new_route))
            # route_types.append(self.create_route_option_transit(new_route))

        return routes, route_types


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
