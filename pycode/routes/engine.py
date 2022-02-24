from typing import List, Optional
import amadeus
import googlemaps
from trippin import tr_db
from trippin.tr_db import Location, Route, TransportationType


# TODO: add error handling
# TODO: remove optional
class RoutesEngine:
    def __init__(self, gmaps_client: googlemaps.Client, amadeus_client: Optional[amadeus.Client] = None):
        self.gmaps_client = gmaps_client
        self.amadeuse_client = amadeus_client

    # TODO: implement
    def creat_route_types_amadeus(self, route: Route) -> List[TransportationType]:
        pass

    # TODO: implement
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

    # TODO: implement
    def creat_route_types_driving(self, route: Route) -> List[TransportationType]:
        return self.creat_route_types_gmaps(route, TransportationType.Type.DRIVING)

    # TODO: implement
    # TODO: add transit type
    # TODO: add legs count to routetype
    def creat_route_types_transit(self, route: Route) -> List[TransportationType]:
        return self.creat_route_types_gmaps(route, TransportationType.Type.TRANSIT)

    # TODO: implement
    def creat_route_types_flight(self, route: Route) -> List[TransportationType]:
        pass

    # TODO: implement
    def create_routes_types(self, route: Route) -> List[TransportationType]:
        pass

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
                drive_type = tr_db.DriveType(distance=first_result['distance']['value'],
                                             duration=first_result['duration']['value'],
                                             legs=1, route=new_route)
                route_types.append(drive_type)

        return routes, route_types
