import dataclasses
from abc import ABC

from trippin.tr_db import Transportation, Airport, GeneralLocation


@dataclasses.dataclass
class RouteData:
    location_0: GeneralLocation
    location_1: GeneralLocation


# transportation: Transportation


@dataclasses.dataclass
class AirportLocationData:
    location: GeneralLocation
    airport: Airport
    transportation: Transportation


@dataclasses.dataclass
class BaseRouteData(ABC):
    transportation: Transportation


@dataclasses.dataclass
class FlightRouteData(BaseRouteData):
    airport_location_0: AirportLocationData
    airport_location_1: AirportLocationData


@dataclasses.dataclass
class DriveRouteData(BaseRouteData):
    pass


@dataclasses.dataclass
class RouteWithOptions:
    route: RouteData
    route_options: List[BaseRouteData]