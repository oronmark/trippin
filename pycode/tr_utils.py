from pathlib import Path
from typing import Any, List, Optional, Dict, Callable
import csv

DEFAULT_ENCODING = 'UTF-8'


def read_from_csv_to_lists(path: Path, encoding: Optional[str] = DEFAULT_ENCODING) -> List[List[Any]]:
    data = []
    with open(path, newline='', encoding=encoding) as file:
        reader = csv.reader(file)
        for row in reader:
            if row:
                data.append(row)
        return data


def read_from_csv_dicts(path: Path, encoding: Optional[str] = DEFAULT_ENCODING) -> List[Dict[str, Any]]:
    data = []
    with open(path, newline='', encoding=encoding) as file:
        reader = csv.reader(file)
        header = next(reader)
        for row in reader:
            if row:
                dictified_row = {header[i]: row[i] for i in range(len(header))}
                data.append(dictified_row)
        return data


def write_to_csv(path: Path, data: List[List[Any]], encoding: Optional[str] = DEFAULT_ENCODING):
    with open(path, 'w+', newline='', encoding=encoding) as file:
        write = csv.writer(file)
        write.writerows(data)


def convert_dict_to_dataclass(data: Dict[Any, Any], class_type, values_converter: Optional[Callable[[Any], Any]] = None):
    # will work only for dataclass with default values
    obj = class_type()
    for field in list(class_type.__dataclass_fields__.keys()):
        setattr(obj, field, data.get(field, None))
    if values_converter:
        obj = values_converter(obj)
    return obj
