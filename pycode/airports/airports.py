from dataclasses import dataclass
import os
from pathlib import Path
from typing import Optional, List, Any, Dict, Tuple
from itertools import product
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
import django

django.setup()
import amadeus
from django.db import transaction
from pycode.tr_enums import *
from pycode.tr_path import tr_path
from pycode.tr_utils import Coordinates, read_from_csv_to_dicts, convert_dict_to_dataclass, calculate_distance_on_map, \
    calculate_flight_stats  # , coordinates_decorator
from trippin import tr_db
from pycode.tr_utils import DEFAULT_BATCH_SIZE
import logging
from amadeus import Client, ResponseError
from django.db.models import Q


# from .airport_data import AirportData, AirportDataDistance, Destination


# TODO: this is a helper class and should be removed
@dataclass
class AirportConnectionData:
    airport_0: tr_db.Airport
    airport_1: tr_db.Airport


@dataclass
class Destination:
    type: str = None
    subtype: str = None
    name: str = None
    iata_code: str = None


@dataclass
class AirportDataDistance:
    airport: tr_db.Airport
    distance: float


# TODO add error handling
# TODO normalize fields names
# TODO check if getting closest airport by distance is a valid choice
# TODO add iterative check in case there are no close airports AIRPORT_DISTANCE_INCREMENTS
# TODO convert to singleton
# TODO divide to levels: continent, region etc for faster results in get_closest_airports
# TODO load once into memory and use a cache and convert to singleton
# TODO add airport distances and flight time to db?
# TODO add condition for closest airport that it is reachable by walk/transit/car
# TODO delete AirportDataDistance, AirportData and AirportConnectionData
class AirportsDAO:
    MAX_AIRPORT_DISTANCE = 200

    def __init__(self, amadeus_client: Optional[amadeus.Client] = None):
        self._amadeus_client = amadeus_client
        self._airports = list(tr_db.Airport.objects.all())  # keeps all airports in memory

    @staticmethod
    def _create_path(path: Optional[Path] = None) -> Path:
        if path:
            return path
        return Path(os.path.join(tr_path.get_resources_path(), AIRPORT_DATA_PATH, AIRPORT_DATA_FILE_NAME))

    @staticmethod
    def _load_data(path: Path) -> List[Dict[str, Any]]:
        def fields_converter(f: str) -> str:
            if f == 'latitude_deg':
                return 'lat'
            if f == 'longitude_deg':
                return 'lng'
            return f

        return read_from_csv_to_dicts(path, header_converter=fields_converter)

    def get_distance_by_airport(self, c: Coordinates) -> List[AirportDataDistance]:
        return [AirportDataDistance(a, calculate_distance_on_map(a, c)) for a in self._airports]

    def get_closest_distances_by_airport(self, c: Coordinates, max_distance: float) -> List[AirportDataDistance]:
        return [a_d for a_d in self.get_distance_by_airport(c) if a_d.distance <= max_distance]

    @classmethod
    def dump_to_db(cls, path: Optional[Path] = None):
        airports_dicts = cls._load_data(cls._create_path(path))
        airports = []
        for a in airports_dicts:
            db_airport = tr_db.Airport(type=a['type'], name=a['name'], lat=a['lat'], lng=a['lng'],
                                       continent=a['continent'], iso_region=a['iso_region'],
                                       iso_country=a['iso_country'],
                                       municipality=a['municipality'], gps_code=a['gps_code'], iata_code=a['iata_code'])
            airports.append(db_airport)

        with transaction.atomic():
            tr_db.Airport.objects.bulk_create(objs=airports, batch_size=DEFAULT_BATCH_SIZE)

    def get_destinations(self, airport: tr_db.Airport) -> List[Destination]:
        try:
            response = self._amadeus_client.airport.direct_destinations.get(departureAirportCode=airport.iata_code).data
            data = [convert_dict_to_dataclass(data=r,
                                              class_type=Destination,
                                              keys_converter=lambda k: 'iata_code' if k == 'iataCode' else k) for r in
                    response]
            return data

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
    def create_airport_connections(self, airport: tr_db.Airport):
        logging.info(f'updating airport connections for {airport.iata_code}')
        destinations_codes = [d.iata_code for d in self.get_destinations(airport)]
        existing_connections_codes = [a.iata_code for a in self._get_all_connected_airports(airport)]

        airports_query = (~Q(iata_code__in=existing_connections_codes)) & \
                         (Q(iata_code__in=destinations_codes) | Q(metropolitan_iata_code__in=destinations_codes))

        other_airports = tr_db.Airport.objects.filter(airports_query)
        logging.info(f'adding {other_airports.count()} new connections for airport {airport}')
        connections = []
        for other_airport in other_airports:
            distance, travel_time = calculate_flight_stats(airport, other_airport)
            connections.append(tr_db.AirportsConnection(airport_0=airport, airport_1=other_airport,
                                                        distance=distance, travel_time=travel_time))

        with transaction.atomic():
            airport.connections_update_time = datetime.now()
            airport.save()
            tr_db.AirportsConnection.objects.bulk_create(objs=connections)

    # TODO: consider changing the use of iata code to id in this case
    @staticmethod
    def _create_airports_connection_query(
            potential_connections: List[Tuple[AirportDataDistance, AirportDataDistance]]) -> Q:
        queries = [Q(airport_0__iata_code=p[0].airport.iata_code, airport_1__iata_code=p[1].airport.iata_code)
                   for p in potential_connections]
        symmetric_queries = [
            Q(airport_0__iata_code=p[1].airport.iata_code, airport_1__iata_code=p[0].airport.iata_code)
            for p in potential_connections]
        queries.extend(symmetric_queries)
        query = queries.pop()
        for q in queries:
            query |= q

        return query

    # TODO: filter out airports that does not fit (e.g not accessible by car)
    # TODO: this is all wrong! remove AirportConnectionData and find another way to calculate this
    def get_connected_airports(self, p0: Coordinates, p1: Coordinates,
                               max_distance: Optional[int] = MAX_AIRPORT_DISTANCE) -> List[AirportConnectionData]:

        closest_airports_0 = self.get_closest_distances_by_airport(p0, max_distance)
        closest_airports_1 = self.get_closest_distances_by_airport(p1, max_distance)

        closest_airports_0_iata_codes = set([al.airport.iata_code for al in closest_airports_0])

        potential_connections = list(product(closest_airports_0, closest_airports_1))

        airport_connections = tr_db.AirportsConnection.objects.filter(
            self._create_airports_connection_query(potential_connections))
        connections_data = []
        for c in airport_connections:
            actual_airport_0, actual_airport_1 = (
                c.airport_0, c.airport_1) if c.airport_0.iata_code in closest_airports_0_iata_codes else (
                c.airport_1, c.airport_0)
            connections_data.append(AirportConnectionData(airport_0=actual_airport_0, airport_1=actual_airport_1))

        return connections_data
