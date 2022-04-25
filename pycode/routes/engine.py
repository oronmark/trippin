import dataclasses
from typing import List
import googlemaps
import django
import logging
from progressbar import progressbar
django.setup()

from trippin import tr_db
from trippin.tr_db import Location, Route, Transportation, Airport, FlightRoute, AirportLocation, \
    DriveRoute, BaseRoute, RouteOption
from pycode.airports.airports import AirportsDAO
from pycode.tr_utils import Coordinates, save_gmaps_result
from .writer import save_route


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

    @dataclasses.dataclass
    class _RouteWithOptions:
        route: tr_db.Route
        route_options: List[tr_db.BaseRoute]

    def __init__(self, gmaps_client: googlemaps.Client, airports_dao: AirportsDAO):
        self._gmaps_client = gmaps_client
        self._airports_dao = airports_dao

    def create_routes_amadeus(self) -> List[Transportation]:
        pass

    # TODO: remove option to write result to file
    def _create_gmaps_transportations(self, p0: Coordinates, p1: Coordinates,
                                      transportation_type: Transportation.Type,
                                      save_to_file: bool = True) -> \
            List[Transportation]:

        transportations = []
        try:
            directions_result = self._gmaps_client.directions((p0.lat, p0.lng),
                                                              (p1.lat, p1.lng),
                                                              mode=transportation_type)

            if save_to_file:
                save_gmaps_result(directions_result, from_name=p0.__str__(), to_name=p1.__str__())

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
        return [DriveRoute(transportation=t) for t in transportations]

    def create_route_option_transit(self, route: Route) -> List[Transportation]:
        pass

    # TODO: add transit to means of transportation
    def create_airport_location(self, airport: Airport, location: Location) -> List[AirportLocation]:
        transportations = self._create_gmaps_transportations(airport, location, Transportation.Type.DRIVING)

        return [AirportLocation(airport=airport, location=location, transportation=t)
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
                                             transportation=transportation))
        return flight_routes

    def create_route_options(self, route: Route) -> List[BaseRoute]:
        flight_routes = self.create_route_option_flight(route)
        drive_routes = self.create_route_option_driving(route)
        return flight_routes + drive_routes

    def create_route(self, location_0: Location, location_1: Location) -> (Route, List[BaseRoute]):
        logging.info(f'creating route for locations locations_0: {location_0}, locations_1: {location_1}')
        new_route = tr_db.Route(location_0=location_0, location_1=location_1)
        route_options = self.create_route_options(new_route)
        return new_route, route_options

    @staticmethod
    def save_route(route: Route, route_options: List[RouteOption]):
        save_route(route, route_options)

    def create_new_routes(self) -> List[_RouteWithOptions]:
        # cannot run in multithreaded mode for now, should be broken into small tasks per route
        new_locations = tr_db.Location.objects.filter(routes_update_time__isnull=True)
        new_routes = []
        for new_location in progressbar(new_locations):
            logging.info(f'creating routes for new location {new_location}')
            for location in progressbar(tr_db.Location.objects.all()):
                if new_location == location:
                    continue
                route, route_options = self.create_route(new_location, location)
                new_routes.append(self._RouteWithOptions(route=route, route_options=route_options))
        return new_routes

    def run_engine(self):
        logging.info('Routes engine is running...')
        routes = self.create_new_routes()
        print('done')
