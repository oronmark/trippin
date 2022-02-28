from typing import List, Optional
import amadeus
import googlemaps
from trippin import tr_db
from trippin.tr_db import Location, Route, TransportationType


# TODO: add error handling
# TODO: remove optional
# TODO: build rout for flight and check if mid routes will work
class RoutesEngine:
    def __init__(self, gmaps_client: googlemaps.Client, amadeus_client: Optional[amadeus.Client] = None):
        self.gmaps_client = gmaps_client
        self.amadeuse_client = amadeus_client

    # TODO: implement
    def creat_route_types_amadeus(self, route: Route) -> List[TransportationType]:
        pass

    def creat_route_types_gmaps(self, route: Route, transportation_type: TransportationType.Type) -> List[
        TransportationType]:

        route_types = []
        directions_result = self.gmaps_client.directions((route.location_0.lat, route.location_0.lng),
                                                         (route.location_1.lat, route.location_1.lng),
                                                         mode=transportation_type.get_string_value())

        if directions_result:
            first_result = directions_result[0]['legs'][0]
            drive_type = tr_db.DriveType(distance=first_result['distance']['value'],
                                         duration=first_result['duration']['value'],
                                         legs=1, route=route)
            route_types.append(drive_type)
        return route_types

    def creat_route_types_driving(self, route: Route) -> List[TransportationType]:
        return self.creat_route_types_gmaps(route, TransportationType.Type.DRIVING)

    # TODO: add transit type
    # TODO: add legs count to routetype
    def creat_route_types_transit(self, route: Route) -> List[TransportationType]:
        return self.creat_route_types_gmaps(route, TransportationType.Type.TRANSIT)

    # TODO: implement
    def create_routes_types(self, route: Route) -> List[TransportationType]:
        pass

    # TODO: implement, for start implement for tlv->new york
    def creat_route_types_flight(self, route: Route) -> List[TransportationType]:
        pass

    def create_routes(self, new_location: Location) -> (List[Route], List[TransportationType]):

        routes = []
        route_types = []
        for location in Location.objects.all():
            new_route = tr_db.Route(location_0=new_location, location_1=location)
            routes.append(new_route)
            route_types.append(self.creat_route_types_driving(new_route))
            route_types.append(self.creat_route_types_transit(new_route))

        return routes, route_types
