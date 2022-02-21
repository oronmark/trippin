from typing import Any, Dict, List

import amadeus
import googlemaps

from pycode import trenums
from trippin import tr_db
from trippin.tr_db import Location, Route
from datetime import datetime
import os


class RoutesEngine:
    def __init__(self, gmaps_client: googlemaps.Client, amadeus_client: amadeus.Client):
        self.gmaps_client = gmaps_client
        self.amadeuse_client = amadeus_client

        def create_routes(new_location: Location) -> List[Route]:
            locations = Location.objects.all().values_list('id', flat=True)

            new_location_lng = new_location.lng
            new_location_lat = new_location.lat
            for location in locations:
                # walking
                # transit
                # driving
                # flight

                directions_result = self.gmaps_client.directions((new_location_lat, new_location_lng), (location.lat,
                                                                                                        location.lng),
                                                                 mode='driving')


