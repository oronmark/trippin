from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, Optional, Dict, Callable, Tuple
import csv
from math import sin, cos, sqrt, atan2, radians

DEFAULT_ENCODING = 'UTF-8'
DEFAULT_BATCH_SIZE = 500


def read_from_csv_to_lists(path: Path, encoding: Optional[str] = DEFAULT_ENCODING) -> List[List[Any]]:
    data = []
    with open(path, newline='', encoding=encoding) as file:
        reader = csv.reader(file)
        for row in reader:
            if row:
                data.append(row)
        return data


def read_from_csv_to_dicts(path: Path, encoding: Optional[str] = DEFAULT_ENCODING) -> List[Dict[str, Any]]:
    data = []
    with open(path, newline='', encoding=encoding) as file:
        reader = csv.reader(file)
        header = next(reader)
        for row in reader:
            if row:
                dictified_row = {header[i]: row[i] for i in range(len(header))}
                data.append(dictified_row)
        return data


# TODO add option to write from dicts
def write_to_csv_from_lists(path: Path, data: List[List[Any]], encoding: Optional[str] = DEFAULT_ENCODING):
    with open(path, 'w+', newline='', encoding=encoding) as file:
        write = csv.writer(file)
        write.writerows(data)


def convert_dict_to_dataclass(data: Dict[Any, Any], class_type,
                              values_converter: Optional[Callable[[Any], Any]] = None) -> Any:
    # will work only for dataclass with default values
    obj = class_type()
    for field in list(class_type.__dataclass_fields__.keys()):
        setattr(obj, field, data.get(field, None))
    if values_converter:
        obj = values_converter(obj)
    return obj


def calculate_distance_on_map(p0: Tuple[float, float], p1: Tuple[float, float]) -> float:
    # this function calculates the distance between 2 points on a map in km
    # this was implemented explicitly because using the geopy.distance function was very slow
    r = 6373.0
    lat1 = radians(p0[0])
    lon1 = radians(p0[1])
    lat2 = radians(p1[0])
    lon2 = radians(p1[1])
    d_lon = lon2 - lon1
    d_lat = lat2 - lat1
    a = sin(d_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(d_lon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = r * c

    return distance


FLIGHT_AVG_SPEED = 750


# this is not an exact answer yet mostly provides a rough estimation
def calculate_flight_time(p0: Tuple[float, float], p1: Tuple[float, float]) -> float:

    return calculate_distance_on_map(p0, p1) / FLIGHT_AVG_SPEED


# this is not an exact answer yet mostly provides a rough estimation
def calculate_flight_time_by_distance(distance: float) -> float:
    return distance / FLIGHT_AVG_SPEED


@dataclass
class Coordinates:
    lat: float
    lng: float
