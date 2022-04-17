from typing import List
import googlemaps
import django
import logging

logging.basicConfig(level=logging.INFO)
django.setup()

from trippin import tr_db
from trippin.tr_db import Location, Route, Transportation, Airport, FlightRoute, AirportLocation, \
    DriveRoute, RouteOption, BaseRoute
from pycode.airports.airports import AirportsDAO
from pycode.tr_utils import Coordinates


# TODO: add error handling, logging and costume exceptions
# TODO: unify all transactions to a single function
# TODO: add tracking bar
# TODO: consider using distance matrix rather the direction
# TODO: add transit type
# TODO: add legs count to route type
# TODO: airport connections is not efficient, refactor
# TODO: currently drive only and only first result, need to expand
# TODO: to start, make another call to google api for arrival from location to airport, instead of using existing routes
# TODO: remove airports dao from init, should be a singleton accessible to engine
# TODO: expand transportations to more types and mark type
# TODO: allow possible tra transportation and not only one to one
class RoutesEngine:

    def __init__(self, gmaps_client: googlemaps.Client, airports_dao: AirportsDAO):
        self._gmaps_client = gmaps_client
        self._airports_dao = airports_dao

    def create_routes_amadeus(self) -> List[Transportation]:
        pass

    def _create_gmaps_transportations(self, p0: Coordinates, p1: Coordinates,
                                      transportation_type: Transportation.Type) -> \
            List[Transportation]:

        transportations = []
        try:
            directions_result = self._gmaps_client.directions((p0.lat, p0.lng),
                                                              (p1.lat, p1.lng),
                                                              mode=transportation_type)

            for d in directions_result:
                result = d['legs'][0]
                transportations.append(tr_db.Transportation(distance=result['distance']['value'],
                                                            duration=result['duration']['value'],
                                                            legs=1))
            return transportations

        except Exception as error:
            raise Exception(f'An error occurred while trying to retrieve directions data with error {error}')

    # TODO: add constraints to enable only viable routes (remove very long distance etc)
    def create_route_option_driving(self, route: Route) -> List[DriveRoute]:
        transportations = self._create_gmaps_transportations(route.location_0, route.location_1,
                                                             Transportation.Type.DRIVING)

       # return [DriveRoute(route=route, transportation=t) for t in transportations]
        return [DriveRoute(transportation=t) for t in transportations]

    def create_route_option_transit(self, route: Route) -> List[Transportation]:
        pass

    # TODO: add transit to means of transportation
    def create_airport_location(self, airport: Airport, location: Location) -> List[AirportLocation]:
        transportations = self._create_gmaps_transportations(airport, location, Transportation.Type.DRIVING)

        return [AirportLocation(airport=airport, location=location, airport_transportation=t)
                for t in transportations]

    def create_route_option_flight(self, route: Route) -> List[FlightRoute]:

        connected_airports = self._airports_dao.get_airport_connections(route.location_0, route.location_1)
        flight_routes = []
        for c in connected_airports:
            airport_location_options_0 = self.create_airport_location(airport=c.airport_0,
                                                                      location=route.location_0)

            airport_location_options_1 = self.create_airport_location(airport=c.airport_1,
                                                                      location=route.location_1)

            if not airport_location_options_0 or not airport_location_options_1:
                logging.info(f'Unable to calculate transportation from for airport, location for '
                             f'({c.airport_0}, {route.location_0.name}) or ({c.airport_1}, {route.location_1.name})')
                continue

            transportation = tr_db.Transportation(distance=c.distance, duration=c.duration,
                                                  legs=c.legs, type=Transportation.Type.FLIGHT)

            flight_routes.append(FlightRoute(airport_location_0=airport_location_options_0[0],
                                             airport_location_1=airport_location_options_1[0],
                                             transportation=transportation,
                                             route=route))
        return flight_routes

    def create_route_options(self, route: Route) -> List[BaseRoute]:
        #flight_routes = self.create_route_option_flight(route)
        flight_routes = []
        drive_routes = self.create_route_option_driving(route)
        return flight_routes + drive_routes

    def create_route(self, location_0: Location, location_1: Location) -> (Route, List[BaseRoute]):
        new_route = tr_db.Route(location_0=location_0, location_1=location_1)
        route_options = self.create_route_options(new_route)
        return new_route, route_options

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

