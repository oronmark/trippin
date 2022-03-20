import argparse
from pathlib import Path
from typing import List, Optional, Dict

import django

django.setup()
from pycode.tr_utils import read_from_csv_to_dicts, write_to_csv_from_lists
from trippin import tr_db
from pycode.tr_path import tr_path
import os


def main():
    print('updating airports')
    path = os.path.join(tr_path.get_resources_path(), 'airportdata', 'airports_with_metroplitan_codes.csv')
    metro_codes = read_from_csv_to_dicts(Path(path))
    metro_codes_by_airport_code = {m['airport_code']: m for m in metro_codes}

    updated_airports = []
    for airport in tr_db.Airport.objects.all():
        airport_metro_data = metro_codes_by_airport_code.get(airport.iata_code, None)
        if airport_metro_data:
            airport.metropolitan_iata_code = airport_metro_data['metropolitan_code']
            updated_airports.append(airport)

    tr_db.Airport.objects.bulk_update(updated_airports, ['metropolitan_iata_code'])

    print('done')



if __name__ == '__main__':
    main()
