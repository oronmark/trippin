from dataclasses import dataclass


# TODO: airports dao should be refactored and make this redundant
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


@dataclass
class Destination:
    type: str = None
    subtype: str = None
    name: str = None
    iata_code: str = None
