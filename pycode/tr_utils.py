from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, Optional, Dict, Callable, Tuple
import csv
from math import sin, cos, sqrt, atan2, radians

from trippin import tr_db
from pycode.airports.airport_data import AirportData

DEFAULT_ENCODING = 'UTF-8'
DEFAULT_BATCH_SIZE = 500


@dataclass
class Coordinates:
    lat: float
    lng: float


def coordinates_decorator(func):
    def inner(*args):
        def convert_to_coordinates(obj: Any) -> Any:
            if isinstance(obj, tr_db.Location):
                return Coordinates(lat=obj.lat, lng=obj.lng)
            if isinstance(obj, tr_db.Airport):
                return Coordinates(lat=obj.latitude_deg, lng=obj.longitude_deg)
            if isinstance(obj, AirportData):
                return Coordinates(lat=obj.latitude_deg, lng=obj.longitude_deg)
            return obj
        return func(*[convert_to_coordinates(a) for a in args])
    return inner


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
                              keys_converter: Optional[Callable[[Any], Any]] = None,
                              values_converter: Optional[Callable[[Any], Any]] = None) -> Any:
    # will work only for dataclass with default values
    obj = class_type()
    if keys_converter:
        data = {keys_converter(k): v for (k, v) in data.items()}
    for field in list(class_type.__dataclass_fields__.keys()):
        setattr(obj, field, data.get(field, None))
    if values_converter:
        obj = values_converter(obj)
    return obj


# def calculate_distance_on_map(p0: Tuple[float, float], p1: Tuple[float, float]) -> float:
#     # this function calculates the distance between 2 points on a map in km
#     # this was implemented explicitly because using the geopy.distance function was very slow
#     r = 6373.0
#     lat1 = radians(p0[0])
#     lon1 = radians(p0[1])
#     lat2 = radians(p1[0])
#     lon2 = radians(p1[1])
#     d_lon = lon2 - lon1
#     d_lat = lat2 - lat1
#     a = sin(d_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(d_lon / 2) ** 2
#     c = 2 * atan2(sqrt(a), sqrt(1 - a))
#     distance = r * c
#
#     return distance


@coordinates_decorator
def calculate_distance_on_map(p0: Coordinates, p1: Coordinates) -> float:
    # this function calculates the distance between 2 points on a map in km
    # this was implemented explicitly because using the geopy.distance function was very slow
    r = 6373.0
    lat0 = radians(p0.lat)
    lon0 = radians(p0.lng)
    lat1 = radians(p1.lat)
    lon1 = radians(p1.lng)
    d_lon = lon1 - lon0
    d_lat = lat1 - lat0
    a = sin(d_lat / 2) ** 2 + cos(lat0) * cos(lat1) * sin(d_lon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = r * c

    return distance


FLIGHT_AVG_SPEED = 750


# this is not an exact answer yet mostly provides a rough estimation
def calculate_flight_time(p0: Coordinates, p1: Coordinates) -> float:
    return calculate_distance_on_map(p0, p1) / FLIGHT_AVG_SPEED


# this is not an exact answer yet mostly provides a rough estimation
def calculate_flight_time_by_distance(distance: float) -> float:
    return distance / FLIGHT_AVG_SPEED


@coordinates_decorator
def calculate_flight_stats(p0: Coordinates, p1: Coordinates) -> (float, float):
    dist = calculate_distance_on_map(p0, p1)
    time = calculate_flight_time_by_distance(dist)
    return dist, time


def sort_attributes(obj, f, attributes):
    values = [getattr(obj, att) for att in attributes]
    values.sort(key=f)
    for att, val in zip(attributes, values):
        setattr(obj, att, val)

