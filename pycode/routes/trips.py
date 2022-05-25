import dataclasses
import datetime
from typing import List, Optional

from .engine import RoutesEngine
from pycode.tr_utils import Coordinates
from trippin import tr_db
from .data_classes import *


class TripEngine:

    def __init__(self):
        pass


# how a trip should be calculated?
# dates - fixed/number of range in days
# aspects by present from trip days
# number of people/ adults, kids etc - later
# preferred mode of transportation - later
# starting/ ending point
# multi country?

# TODO: verify aspects
# TODO: create actual days
# TODO: for start, allow only 1 dest country
# TODO: for start, allow only an absolute single date range
# TODO : assume driving time is not more the 3 hours in the request
# TODO : assume src_country != dest_country
class TripRequest:
    @dataclasses.dataclass
    class AspectData:
        aspect_type: tr_db.Interest.Aspect
        capacity: int

    def __init__(self, aspects: List[AspectData], src_country: Optional[str], dest_country: str,
                 days: Optional[int], start_date: datetime.date, end_date: datetime.date,
                 soft_range_days: Optional[int], src_point: Coordinates, dest_point: Coordinates,
                 dest_location: tr_db.Location,
                 transportation_type: List[tr_db.Transportation.type], seasons: Optional[str],
                 routes_engine: RoutesEngine):
        self.aspects = aspects  # for now, assume sum of capacity is 100
        # self.src_country = src_country
        self.dest_country = dest_country  # the county of the vacation (currently single country)
        self.start_date = start_date
        self.end_date = end_date
        self.transportation_type = transportation_type
        self.max_transportation = 3  # hours
        self.src_point = src_point
        self.dest_point = dest_point
        self.route_engine = routes_engine
        self.dest_location = dest_location # currently insert manually

    # TODO: construct user location in some other way (implicitly)
    def calc_starting_point_to_dest_point(self):
        src_location = tr_db.UserLocation(lat=self.src_point.lat, lng=self.src_point.lng)
        route_with_options: RouteWithOptions = self.route_engine.create_route(src_location, self.dest_location)


    # first arrive to dest country with starting point
    # get all locations with any of the aspects (with equal or more for each of the aspects?)
    # create a greedy algorithm and try to answer each of the aspects
    # def calc_trips(self) -> List[tr_db.Trip]:
    #     total_days = self.end_date - self.start_date
