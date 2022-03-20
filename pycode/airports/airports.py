import os
from pathlib import Path
from typing import Optional, List, Any, Dict, Tuple
from itertools import product
from datetime import datetime
import django

django.setup()
import amadeus
from django.db import transaction
from pycode.tr_enums import *
from pycode.tr_path import tr_path
from pycode.tr_utils import Coordinates, read_from_csv_to_dicts, convert_dict_to_dataclass, calculate_distance_on_map, \
    calculate_flight_time_by_distance, coordinates_decorator
from trippin import tr_db
from pycode.tr_utils import DEFAULT_BATCH_SIZE
import logging
from amadeus import Client, ResponseError
from django.db.models import Q
from .airport_data import AirportData, AirportDataDistance


# TODO add error handling
# TODO normalize filed names
# TODO check if getting closest airport by distance is a valid choice
# TODO move max_distance const to somewhere else
# TODO add iterative check in case there are no close airports AIRPORT_DISTANCE_INCREMENTS
# TODO check if airport by coordinates is needed
# TODO refactor init
# TODO convert to singleton
# TODO divide to levels: continent, region etc for faster results in get_closest_airports
# TODO load once into memory and use a cache and convert to singleton
# TODO add airport distances and flight time to db?
# TODO add condition for closest airport that it is reachable by walk/transit/car
# TODO delete AirportDataDistance and AirportData
class AirportsDAO:
    AirportType = AirportData | tr_db.Airport
    MAX_AIRPORT_DISTANCE = 200

    def __init__(self, amadeus_client: Optional[amadeus.Client] = None, path: Optional[Path] = None):
        self._amadeus_client = amadeus_client
        self._path = self._create_path(path)
        airports_data = self._load_data(self._path)
        self._airports: List[AirportData] = self._create_airports(airports_data)
        self._airport_by_coordinates = self._create_airports_by_coordinates()
        self.airports_by_iata_code = self._create_airports_by_iata_code()

    @staticmethod
    def _create_path(path: Optional[Path] = None) -> Path:
        if path:
            return path
        return Path(os.path.join(tr_path.get_resources_path(), AIRPORT_DATA_PATH, AIRPORT_DATA_FILE_NAME))

    @staticmethod
    def _load_data(path: Path) -> List[Dict[str, Any]]:
        return read_from_csv_to_dicts(path)

    @staticmethod
    def _create_airports(airports_data: List[Dict[str, Any]]) -> List[AirportData]:

        def _convert_coordinates_to_float(a: AirportData) -> AirportData:
            a.latitude_deg = float(a.latitude_deg)
            a.longitude_deg = float(a.longitude_deg)
            return a

        airports = [convert_dict_to_dataclass(a, AirportData,
                                              values_converter=_convert_coordinates_to_float) for a in airports_data]

        return airports

    def _create_airports_by_coordinates(self) -> Dict[Tuple[float, float], AirportData]:
        return {(a.latitude_deg, a.longitude_deg): a for a in self._airports}

    def _create_airports_by_iata_code(self) -> Dict[str, AirportData]:
        return {a.iata_code: a for a in self._airports}

    def get_airport_by_coordinates(self, lat: float, lng: float) -> Optional[AirportData]:
        return self._airport_by_coordinates.get((lat, lng), None)

    @coordinates_decorator
    def get_distance_by_airport(self, c: Coordinates) -> List[AirportDataDistance]:
        return [AirportDataDistance(a, calculate_distance_on_map(a, c)) for a in self._airports]

    def get_closest_distances_by_airport(self, c: Coordinates, max_distance: float) -> List[AirportDataDistance]:
        return [a_d for a_d in self.get_distance_by_airport(c) if a_d.distance <= max_distance]

    def get_airport_by_iata_code(self, iata_code: str) -> Optional[AirportType]:
        return self.airports_by_iata_code.get(iata_code, None)

    @classmethod
    def dump_to_db(cls, path: Optional[Path] = None):
        airports_dicts = cls._load_data(cls._create_path(path))
        airports_data = cls._create_airports(airports_dicts)
        airports = []
        for a in airports_data:
            db_airport = tr_db.Airport(id=a.id, type=a.type, name=a.name, latitude_deg=a.latitude_deg,
                                       longitude_deg=a.longitude_deg,
                                       continent=a.continent, iso_region=a.iso_region, iso_country=a.iso_country,
                                       municipality=a.municipality, gps_code=a.gps_code, iata_code=a.iata_code)
            airports.append(db_airport)

        with transaction.atomic():
            tr_db.Airport.objects.bulk_create(objs=airports, batch_size=DEFAULT_BATCH_SIZE)

    @staticmethod
    def get_airports_by_airport_data(airports_data: List[AirportData]) -> List[tr_db.Airport]:
        # TODO: this implementation is temporary, this data will be pre-loaded with the dao
        return tr_db.Airport.objects.filter(id__in=[a.id for a in airports_data])

    def get_destinations_iata_code(self, airport: tr_db.Airport) -> List[str]:
        try:
            response = self._amadeus_client.airport.direct_destinations.get(departureAirportCode=airport.iata_code)
            print('gasgs')
            return [a['iataCode'] for a in response.data]
        except ResponseError as error:
            raise Exception(
                f'An error occurred while trying to fetch all linked airports, airport_code: ${airport.iata_code}, '
                f'error: ${error}'
            )

    # TODO: add prefetch to perform less queries, this is not efficient!
    @staticmethod
    def _get_all_connected_airports(airport: tr_db.Airport) -> List[tr_db.Airport]:
        connections = tr_db.AirportsConnection.objects.filter(Q(airport_0=airport) | Q(airport_1=airport))
        other_airports = []
        for c in connections:
            if c.airport_0 == airport:
                other_airports.append(c.airport_1)
            else:
                other_airports.append(c.airport_0)
        return other_airports

    # TODO: preform db transaction somewhere else
    # TODO: update airport update
    # TODO: remove duplicate  connections
    def create_airport_connections(self, airport: tr_db.Airport):
        logging.info(f'updating airport connections for {airport.iata_code}')
        other_airports_iata_code = set()
        for d in self.get_destinations_iata_code(airport):
            other_airport_data = self.get_airport_by_iata_code(d)
            if other_airport_data:
                other_airports_iata_code.add(other_airport_data.iata_code)
            else:
                logging.info(f'Unable to create connection ({airport},{d}), '
                             f'could not find airport in db')

        existing_connections_codes = set([a.iata_code for a in self._get_all_connected_airports(airport)])
        other_airports_iata_code -= existing_connections_codes

        other_airports = tr_db.Airport.objects.filter(iata_code__in=other_airports_iata_code)
        connections = []
        for other_airport in other_airports:
            distance = calculate_distance_on_map(airport, other_airport)
            travel_time = calculate_flight_time_by_distance(distance)
            connections.append(tr_db.AirportsConnection(airport_0=airport, airport_1=other_airport,
                                                        distance=distance, travel_time=travel_time))

        with transaction.atomic():
            airport.connections_update_time = datetime.now()
            airport.save()
            tr_db.AirportsConnection.objects.bulk_create(objs=connections)

    @staticmethod
    def _create_airports_connection_query(
            potential_connections: List[Tuple[AirportDataDistance, AirportDataDistance]]) -> Q:
        queries = [Q(airport_0_id=p[0].airport_data.id, airport_1_id=p[1].airport_data.id)
                   for p in potential_connections]
        symmetric_queries = [Q(airport_0_id=p[1].airport_data.id, airport_1_id=p[0].airport_data.id)
                             for p in potential_connections]
        queries.extend(symmetric_queries)
        query = queries.pop()
        for q in queries:
            query |= q

        return query

    # TODO: filter out airports that does not fit (e.g not accessible by car)
    # TODO: should be optimized, remove redundant options
    @coordinates_decorator
    def get_connected_airports(self, p0: Coordinates, p1: Coordinates,
                               max_distance: Optional[int] = MAX_AIRPORT_DISTANCE) -> List[tr_db.AirportsConnection]:

        closest_airports_0 = self.get_closest_distances_by_airport(p0, max_distance)
        closest_airports_1 = self.get_closest_distances_by_airport(p1, max_distance)
        potential_connections = list(product(closest_airports_0, closest_airports_1))

        return tr_db.AirportsConnection.objects.filter(self._create_airports_connection_query(potential_connections))




def main():
    # new york
    # "lat": 40.7127753,
    # "lng": -74.0059728
    p0 = Coordinates(lat=40.7127753, lng=-74.0059728)

    # afula
    # "lat": 32.6104931,
    # "lng": 35.287922
    p1 = Coordinates(lat=32.6104931, lng=35.287922)
    airports_dao = AirportsDAO()
    ans = airports_dao.get_connected_airports(p0, p1)


if __name__ == '__main__':
    main()
