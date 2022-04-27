import dataclasses
import datetime
from typing import List, Optional

from trippin import tr_db


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


class TripRequest:
    @dataclasses.dataclass
    class AspectData:
        aspect_type: tr_db.Interest.Aspect
        capacity: int

    def __init__(self, aspect: List[AspectData], source_country: str, dest_countries: List[str],
                 days: Optional[int], date_ranges: List[(datetime.date, datetime.date)], soft_range_days: Optional[int],
                 transportation_type: List[tr_db.Transportation.type], seasons: Optional[str]):
        pass
        # verify aspects
        # create actual days


class TripSegment:
    pass
    # location
    # date ranges
    # contribution by aspect
    # next segment
    # route to next location?


class TripOption:
    pass
    # date ranges
    # segments

