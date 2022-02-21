from typing import Any, Dict, List, Optional

import amadeus
import googlemaps

from pycode import trenums
from trippin import tr_db
from trippin.tr_db import Location, Route, TransportationType
from datetime import datetime
import os


# TODO: first, add driving only
# TODO: add error handling
# TODO: remove optional
class RoutesEngine:
    def __init__(self, gmaps_client: googlemaps.Client, amadeus_client: Optional[amadeus.Client] = None):
        self.gmaps_client = gmaps_client
        self.amadeuse_client = amadeus_client

    def create_routes(self, new_location: Location) -> (List[Route], List[TransportationType]):

        new_location_lng = new_location.lng
        new_location_lat = new_location.lat
        routes = []
        route_types = []
        for location in Location.objects.all():
            new_route = tr_db.Route(location_0=new_location, location_1=location)
            routes.append(new_route)
            directions_result = self.gmaps_client.directions((new_location_lat, new_location_lng), [location.lat,
                                                                                                    location.lng],
                                                             mode='driving')

            if directions_result:
                first_result = directions_result[0]['legs'][0]
                drive_type = tr_db.DriveType(distance=first_result['distance'], duration=first_result['duration'],
                                             legs=1, route=new_route)
                route_types.append(drive_type)

        return routes, route_types
