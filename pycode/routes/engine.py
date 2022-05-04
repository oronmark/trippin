import dataclasses
from typing import List, Dict, Any
import googlemaps
import django
import logging
from progressbar import progressbar
from datetime import datetime
django.setup()
from trippin import tr_db
from trippin.tr_db import Location, Route, Transportation, Airport, FlightRoute, AirportLocation, \
    DriveRoute, BaseRoute, RouteOption, GeneralLocation, UserLocation
from trippin.pycode import tr_utils
from pycode.airports.airports import AirportsDAO
from pycode.tr_utils import Coordinates
from .writer import save_route
from enum import Enum, auto
from pathlib import Path
from trippin.pycode.tr_path import tr_path
from collections import defaultdict

# TODO: add error handling, logging and costume exceptions
# TODO: consider using distance matrix rather the direction
# TODO: add transit type
# TODO: add legs count to route type
# TODO: airport connections is not efficient, refactor
# TODO: currently drive only and only first result, need to expand
# TODO: to start, make another call to google api for arrival from location to airport, instead of using existing routes
# TODO: expand transportations to more types and mark type
# TODO: allow possible transportation and not only one to one


class RoutesEngine:

    # TODO: will be removed during dev
    class GmapsMode(Enum):
        LOCAL_READ = auto()
        LOCAL_WRITE = auto()
        FULLY_LOCAL = auto()
        FULLY_REMOTE = auto()

        def is_local_read(self) -> bool:
            return self == self.LOCAL_READ or self == self.FULLY_LOCAL

        def is_local_write(self) -> bool:
            return self == self.LOCAL_WRITE or self == self.FULLY_LOCAL

    @dataclasses.dataclass
    class _RouteWithOptions:
        route: tr_db.Route
        route_options: List[tr_db.BaseRoute]

    def __init__(self, gmaps_client: googlemaps.Client, airports_dao: AirportsDAO, gmaps_mode: GmapsMode = GmapsMode.LOCAL_READ):
        self._gmaps_client = gmaps_client
        self._airports_dao = airports_dao
        self._gmaps_mode = gmaps_mode

    def create_routes_amadeus(self) -> List[Transportation]:
        pass

    def _create_gmaps_transportations(self, p0: Coordinates, p1: Coordinates, transportation_type: Transportation.Type) -> \
            List[Transportation]:

        def _create_gmaps_resources_path(from_name: str, to_name: str, path: Path = None) -> Path:
            from_name, to_name = (from_name, to_name) if from_name < to_name else (to_name, from_name)
            return path or Path.joinpath(tr_path.get_resources_path(), 'gmaps_directions_results',
                                         f'{from_name}_to_{to_name}.json')

        def _save_gmaps_result(data: Dict[Any, Any], path: Path = None):
            path = _create_gmaps_resources_path(p0.__str__(), p1.__str__(), path)
            tr_utils.write_to_json_from_dicts(data, path)

        def _load_or_query_gmaps_results(path: Path = None) -> Dict[Any, Any]:
            path = _create_gmaps_resources_path(p0.__str__(), p1.__str__(), path)
            if path.exists() and self._gmaps_mode.is_local_read():
                return tr_utils.read_from_json_to_dicts(path)
            logging.info(f'Querying gmaps directions api for {p0.__str__()} to {p1.__str__()}')
            return self._gmaps_client.directions((p0.lat, p0.lng), (p1.lat, p1.lng), mode=transportation_type)

        transportations = []
        try:
            directions_result = _load_or_query_gmaps_results()
            if self._gmaps_mode.is_local_write():
                _save_gmaps_result(directions_result)

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

    # TODO: consider not using _RouteWithOptions replace with simpler ds
    def create_new_routes(self) -> List[_RouteWithOptions]:
        # cannot run in multithreaded mode for now, should be broken into small tasks per route
        new_locations = tr_db.Location.objects.filter(routes_update_time__isnull=True)
        location_to_other_locations = defaultdict(lambda: set())
        new_routes = []
        for new_location in progressbar(new_locations, prefix='new location: '):
            logging.info(f'creating routes for new location {new_location}')
            for other_location in progressbar(Location.objects.all(),  prefix='other locations: '):
                if new_location == other_location or new_location in location_to_other_locations[other_location]:
                    continue
                route, route_options = self.create_route(new_location, other_location)
                new_routes.append(self._RouteWithOptions(route=route, route_options=route_options))
                location_to_other_locations[new_location].add(other_location)
                location_to_other_locations[other_location].add(new_location)
        return new_routes

    def run_engine(self):
        logging.info('Routes engine is running...')
        route_with_options = self.create_new_routes()
        for rwo in route_with_options:
            save_route(rwo.route, rwo.route_options)
        logging.info('Updating locations update time')
        Location.objects.update(routes_update_time=datetime.now())
        logging.info('Routes engine finished successfully')

