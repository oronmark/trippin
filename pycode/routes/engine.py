from typing import List, Optional
import amadeus
import googlemaps
from amadeus import Client, ResponseError
import os
import django
import logging
logging.basicConfig(level=logging.INFO)
django.setup()

from trippin import tr_db
from trippin.tr_db import Location, Route, Transportation, Airport, AirportConnection
from pycode.airports.airports import AirportsDAO
from django.db import transaction


# TODO: add error handling, logging and costume exceptions
# TODO: remove optional
# TODO: build route for flight and check if mid routes will work
# TODO: unify all transactions to a single function
# TODO: add tracking bar
class RoutesEngine:

    MAX_AIRPORT_DISTANCE = 200
    DEFAULT_BATCH_SIZE = 500

    def __init__(self, gmaps_client: googlemaps.Client, airports_dao: AirportsDAO,
                 amadeus_client: Optional[amadeus.Client] = None):
        self.gmaps_client = gmaps_client
        self.amadeuse_client = amadeus_client
        self.airports_dao = airports_dao

    # TODO: implement
    def create_routes_amadeus(self, route: Route) -> List[Transportation]:
        pass

    def create_route_gmaps(self, route: Route, transportation_type: Transportation.Type) -> List[
        Transportation]:

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

    def create_route_option_driving(self, route: Route) -> List[Transportation]:
        return self.create_route_gmaps(route, Transportation.Type.DRIVING)

    # TODO: add transit type
    # TODO: add legs count to routetype
    def create_route_option_transit(self, route: Route) -> List[Transportation]:
        return self.create_route_gmaps(route, Transportation.Type.TRANSIT)

    # TODO: implement
    def create_routes_options(self, route: Route) -> List[Transportation]:
        pass

    # TODO: implement, for start implement for tlv->new york
    # find closest airport for each location
    # check from closes to furthers airport if the flight is possible
    # add sub route to airport?
    # first, calculate route for closest airport
    def create_route_option_flight(self, route: Route) -> List[Transportation]:
        closest_airports_0 = self.airports_dao.get_closest_distances_by_airport(route.location_0,
                                                                                self.MAX_AIRPORT_DISTANCE)
        closest_airports_1 = self.airports_dao.get_closest_distances_by_airport(route.location_1,
                                                                                self.MAX_AIRPORT_DISTANCE)
        closest_airport_0 = min(closest_airports_0, key=lambda a: a.distance)
        closest_airport_1 = min(closest_airports_1, key=lambda a: a.distance)

        if not closest_airports_0 or not closest_airports_1:
            raise Exception('Could not find any airport close enough to location')

    def create_routes(self, new_location: Location) -> (List[Route], List[Transportation]):

        routes = []
        route_types = []
        for location in Location.objects.all():
            new_route = tr_db.Route(location_0=new_location, location_1=location)
            routes.append(new_route)
            route_types.append(self.create_route_option_driving(new_route))
            route_types.append(self.create_route_option_transit(new_route))

        return routes, route_types

    def get_destinations_iata_code(self, airport: Airport) -> List[str]:
        try:
            response = self.amadeuse_client.airport.direct_destinations.get(departureAirportCode='TLV')
            return [a['iataCode'] for a in response.data]
        except ResponseError as error:
            raise Exception(
                f'An error occurred while trying to fetch all linked airports, airport_code: ${airport.iata_code}, '
                f'error: ${error}'
            )

    # TODO: not efficient, refactor
    def create_airport_routes(self, airport: Airport):
        logging.info(f'creating airport routes for ${airport.iata_code}')
        airports_data = []
        for d in self.get_destinations_iata_code(airport):
            other_airport_code = self.airports_dao.get_airport_by_iata_code(d)
            if other_airport_code:
                airports_data.append(other_airport_code)

        other_airports = Airport.objects.filter(iata_code__in=[code.iata_code for code in airports_data])
        routes = [AirportConnection(airport_0=airport, airport_1=a) for a in other_airports.all()]

        with transaction.atomic():
            tr_db.AirportConnection.objects.bulk_create(objs=routes)


def main():
    airport_codes_subset_for_test = ['TLV', 'JFK', 'EWR', 'LAS', 'ATH', 'SKG']
   # airport_codes_subset_for_test = ['TLV']
    amadeus = Client(
        client_id=os.environ['AMADEUS_API_KEY'],
        client_secret=os.environ['AMADEUS_API_SECRET'],
        hostname='test'
    )
    gmaps = googlemaps.Client(key=os.environ['API_KEY'])
    airports_dao = AirportsDAO()
    routes_engine = RoutesEngine(gmaps_client=gmaps, amadeus_client=amadeus, airports_dao=airports_dao)


    # attempt to add airports routs for test airports
    for code in airport_codes_subset_for_test:
        airport = tr_db.Airport.objects.filter(iata_code=code).get()
        routes_engine.create_airport_routes(airport)

    print('done')


if __name__ == '__main__':
    main()
