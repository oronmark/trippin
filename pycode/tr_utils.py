from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, Optional, Dict, Callable
import csv
from math import sin, cos, sqrt, atan2, radians
import json
from trippin.pycode.tr_path import tr_path

DEFAULT_ENCODING = 'UTF-8'
DEFAULT_BATCH_SIZE = 500
TR_ID = int


@dataclass
class Coordinates:
    lat: float
    lng: float


def read_from_csv_to_lists(path: Path, encoding: Optional[str] = DEFAULT_ENCODING) -> List[List[Any]]:
    data = []
    with open(path, newline='', encoding=encoding) as file:
        reader = csv.reader(file)
        for row in reader:
            if row:
                data.append(row)
        return data


def read_from_csv_to_dicts(path: Path, encoding: Optional[str] = DEFAULT_ENCODING,
                           header_converter: Optional[Callable[[str], str]] = None) -> List[Dict[str, Any]]:
    data = []
    with open(path, newline='', encoding=encoding) as file:
        reader = csv.reader(file)
        header = next(reader)
        if header_converter:
            header = [header_converter(h) for h in header]
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


# @coordinates_decorator
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


def calculate_flight_stats(p0: Coordinates, p1: Coordinates) -> (float, float):
    dist = calculate_distance_on_map(p0, p1)
    time = calculate_flight_time_by_distance(dist)
    return dist, time


def sort_attributes(obj, f, attributes):
    values = [getattr(obj, att) for att in attributes]
    values.sort(key=f)
    for att, val in zip(attributes, values):
        setattr(obj, att, val)


def write_to_json_from_dicts(data: Dict[Any, Any], path: Path):
    with open(path, 'w+') as fp:
        json.dump(data, fp)


def read_from_json_to_dicts(path: Path) -> Dict[Any, Any]:
    with open(path) as json_file:
        return json.load(json_file)


