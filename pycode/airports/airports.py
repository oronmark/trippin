from pathlib import Path
from typing import Optional, List, Any, Dict
import os
from pycode.tr_enums import *
from pycode.tr_utils import read_from_csv_dicts
from pycode.tr_path import tr_path


# TODO check if static method is needed
# TODO add error handling
class AirportsDAO:

    def __init__(self, path: Optional[Path] = None):
        self.path = self._create_path(path)
        self.data = None

    def init(self):
        self.data = self._load_data()

    def get_data(self):
        return self.data

    @staticmethod
    def _create_path(path: Optional[Path] = None):
        if path:
            return path
        return os.path.join(tr_path.get_resources_path(), AIRPORT_DATA_PATH, AIRPORT_DATA_FILE_NAME)

    def _load_data(self):
        print('sdgdsg')
        data: List[Dict[Any]] = read_from_csv_dicts(self.path)
        return data





def main():
    airports_dao = AirportsDAO()
    airports_dao.init()
    data = airports_dao.get_data()
    print('bla')



if __name__ == '__main__':
    main()
