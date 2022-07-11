import django
django.setup()

import dataclasses
import datetime
from collections import defaultdict
from typing import List, Optional, Set, Dict

from engine import RoutesEngine
from pycode.tr_utils import Coordinates
from trippin import tr_db
from data_classes import *


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

# TODO : verify aspects
# TODO : create actual days
# TODO : for start, allow only 1 dest country
# TODO : for start, allow only an absolute single date range
# TODO : assume driving time is not more the 3 hours in the request
# TODO : assume src_country != dest_country
# TODO : assume dest county is part of input
class TripRequest:
    @dataclasses.dataclass
    class AspectData:
        aspect_type: tr_db.Interest.Aspect
        capacity: int

    def __init__(self, aspects: List[AspectData], src_country: Optional[str], dest_country: str,
                 days: Optional[int], start_date: datetime.date, end_date: datetime.date,
                 soft_range_days: Optional[int], src_coord: Coordinates, dest_coord: Coordinates,
                 dest_location: tr_db.Location,
                 transportation_type: List[tr_db.Transportation.Type],
                 # seasons: Optional[str],
                 routes_engine: RoutesEngine):
        self.aspects = aspects  # for now, assume sum of capacity is 100
        # self.src_country = src_country
        self.dest_country = dest_country  # the county of the vacation (currently single country)
        self.start_date = start_date
        self.end_date = end_date
        self.transportation_type = transportation_type
        self.max_transportation = 3  # hours
        self.src_coord = src_coord
        self.dest_coord = dest_coord
        self.route_engine = routes_engine
        self.dest_location = dest_location # currently insert manually

    # TODO: construct user location in some other way (implicitly), why though? past Oron is weird
    def calc_starting_point_to_dest_point(self) -> RouteWithOptionsData:
        src_user_location = tr_db.UserLocation(lat=self.src_coord.lat, lng=self.src_coord.lng)
        route_with_options: RouteWithOptionsData = self.route_engine.route_with_options(src_user_location, self.dest_location)
        return route_with_options

    @classmethod
    def get_locations_by_aspects(cls) -> Dict[tr_db.Interest.Aspect, Set[tr_db.Location]]:
        # aspects_names = [a.aspect_type for a in self.aspects]
        aspects_names = [tr_db.Interest.Aspect.BEACH, tr_db.Interest.Aspect.HISTORY]
        # relevant_locations = tr_db.Location.objects.filter(country=self.dest_country, interests__aspect__in=aspects_names)
        relevant_locations = tr_db.Location.objects.filter(country='GR',
                                                           interests__aspect__in=aspects_names)
        locations_by_aspects = defaultdict(lambda: set())
        for location in relevant_locations:
            aspects_for_location = location.interests.values_list('aspect', flat=True)
            for aspect in aspects_for_location:
                locations_by_aspects[aspect].add(location)

        return locations_by_aspects




    # first arrive to dest country with starting point
    # get all locations with any of the aspects (with equal or more for each of the aspects?)
    # create a greedy algorithm and try to answer each of the aspects
    # def calc_trips(self) -> List[tr_db.Trip]:
    #     total_days = self.end_date - self.start_date
    # algo suggestion:
    # get all locations in same country by aspect
    # pick start walking the route by distance and remove answered aspects


def main():
    ans = TripRequest.get_locations_by_aspects()
    print('asfsaf')


if __name__ == '__main__':
    main()