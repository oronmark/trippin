import math
from pathlib import Path
from typing import Optional, List, Any, Dict, Tuple
import os
from pycode.tr_enums import *
from pycode.tr_utils import read_from_csv_dicts, convert_dict_to_dataclass, calculate_distance_on_map
from pycode.tr_path import tr_path
from dataclasses import dataclass


@dataclass
class Airport:
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


# TODO add error handling
# TODO normalize filed names
# TODO check if getting closest airport by distance is a valid choice
# TODO move max_distance const to somewhere else
class AirportsDAO:
    MAX_AIRPORT_DISTANCE = 200

    def __init__(self, path: Optional[Path] = None):
        self._path = self._create_path(path)
        self._airports: List[Airport] = self._create_airports()
        self._airport_by_coordinates = self._create_airports_by_coordinates()

    @staticmethod
    def _create_path(path: Optional[Path] = None) -> Path:
        if path:
            return path
        return Path(os.path.join(tr_path.get_resources_path(), AIRPORT_DATA_PATH, AIRPORT_DATA_FILE_NAME))

    def _load_data(self) -> List[Dict[str, Any]]:
        return read_from_csv_dicts(self._path)

    def _create_airports(self) -> List[Airport]:

        def _convert_coordinates_to_float(a: Airport) -> Airport:
            a.latitude_deg = float(a.latitude_deg)
            a.longitude_deg = float(a.longitude_deg)
            return a

        airports = []
        for airport_dict in self._load_data():
            airport: Airport = convert_dict_to_dataclass(airport_dict, Airport,
                                                         values_converter=_convert_coordinates_to_float)
            airports.append(airport)

        return airports

    def _create_airports_by_coordinates(self) -> Dict[Tuple[float, float], Airport]:
        return {(a.latitude_deg, a.longitude_deg): a for a in self._airports}

    def get_airport_by_coordinates(self, lat: float, lng: float) -> Optional[Airport]:
        return self._airport_by_coordinates.get((lat, lng), None)

    def get_closest_airports(self, lat: float, lng: float) -> List[Airport]:
        return [airport for airport in self._airports if calculate_distance_on_map((lat, lng), (
            airport.latitude_deg, airport.longitude_deg)) < AirportsDAO.MAX_AIRPORT_DISTANCE]

def main():
    airports_dao = AirportsDAO()
    import time
    start = time.time()
    closest_airports = airports_dao.get_closest_airports(lat=32.6104931, lng=35.287922)
    end = time.time()
    print(end-start)


if __name__ == '__main__':
    main()
