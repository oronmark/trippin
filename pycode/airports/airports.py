from pathlib import Path
from typing import Optional, List, Any, Dict
import os
from pycode.tr_enums import *
from pycode.tr_utils import read_from_csv_dicts, convert_dict_to_dataclass
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


# TODO check if static method is needed
# TODO add error handling
# TODO convert to private
# TODO normalize filed names
class AirportsDAO:

    def __init__(self, path: Optional[Path] = None):
        self.path = self._create_path(path)
        self.airports = self.create_airports()
        self.airport_by_iata = None

    @staticmethod
    def _create_path(path: Optional[Path] = None):
        if path:
            return path
        return os.path.join(tr_path.get_resources_path(), AIRPORT_DATA_PATH, AIRPORT_DATA_FILE_NAME)

    def _load_data(self):
        data: List[Dict[Any]] = read_from_csv_dicts(self.path)
        return data

    def create_airports(self):
        airports = []
        for airport_dict in self._load_data():
            airports.append(convert_dict_to_dataclass(airport_dict, Airport))

        return airports



# def main():
#     airports_dao = AirportsDAO()
#     data = airports_dao.get_data()
#     print('bla')
#
#
#
# if __name__ == '__main__':
#     main()
