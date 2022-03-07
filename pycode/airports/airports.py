import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Any, Dict, Tuple
from django.db import transaction
from pycode.tr_enums import *
from pycode.tr_path import tr_path
from pycode.tr_utils import read_from_csv_to_dicts, convert_dict_to_dataclass, calculate_distance_on_map
from trippin import tr_db


@dataclass
class AirportData:
    id: str = None
    type: str = None
    name: str = None
    latitude_deg: float = None
    longitude_deg: float = None
    continent: str = None
    iso_region: str = None
    iso_country: str = None
    municipality: str = None
    gps_code: str = None
    iata_code: str = None


@dataclass
class AirportDataDistance:
    airport_data: AirportData
    distance: float


# TODO add error handling
# TODO normalize filed names
# TODO check if getting closest airport by distance is a valid choice
# TODO move max_distance const to somewhere else
# TODO add iterative check in case there are no close airports AIRPORT_DISTANCE_INCREMENTS
# TODO check if airport by coordinates is needed
# TODO refactor init
# TODO convert to singleton
# TODO divide to levels: continent, region etc for faster results in get_closest_airports
# TODO load once into memory and use a cache
class AirportsDAO:
    AirportType = AirportData | tr_db.Airport

    def __init__(self, path: Optional[Path] = None):
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

    def get_distance_by_airport(self, lat: float, lng: float) -> List[AirportDataDistance]:
        return [AirportDataDistance(a, calculate_distance_on_map((a.latitude_deg, a.longitude_deg), (lat, lng))) for a
                in self._airports]

    def get_distance_by_airport_for_location(self, location: tr_db.Location) -> List[AirportDataDistance]:
        return self.get_distance_by_airport(lat=location.lat, lng=location.lng)

    def get_closest_distances_by_airport(self, location: tr_db.Location, max_distance: float) -> List[
            AirportDataDistance]:
        return [a_d for a_d in self.get_distance_by_airport_for_location(location) if a_d.distance <= max_distance]

    def get_airport_by_iata_code(self, iata_code: str) -> Optional[AirportType]:
        return self.airports_by_iata_code.get(iata_code, None)

    @classmethod
    def dump_csv_to_db(cls, path: Optional[Path] = None):
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
            tr_db.Airport.objects.bulk_create(objs=airports, batch_size=cls.DEFAULT_BATCH_SIZE)
