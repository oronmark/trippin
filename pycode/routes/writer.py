from typing import Dict, List
from functools import reduce
import logging
from django.db.models import Q

from trippin.tr_db import Route, FlightRoute, AirportLocation, DriveRoute, RouteOption

logging.basicConfig(level=logging.INFO)
from django.db import transaction
from trippin.pycode.tr_utils import TR_ID
from multipledispatch import dispatch


# TODO: change input to flight route and not airport location
def create_airport_location_query(flight_route: FlightRoute):
    airport_location_queries = [Q(airport_id=al.airport_id, location_id=al.location_id) for al in
                                flight_route.get_airport_locations()]
    return reduce(lambda alq0, alq1: alq0 | alq1, airport_location_queries)


def get_or_create_airport_location(airport_location: AirportLocation,
                                   existing_airport_locations) -> AirportLocation:
    # existing_airport_locations: Dict[(TR_ID, TR_ID), AirportLocation]) -> AirportLocation:
    existing_airport_location = existing_airport_locations.get(
        (airport_location.airport_id, airport_location.location_id), None)
    if existing_airport_location:
        return existing_airport_location
    else:
        airport_location.transportation.save()
        airport_location.save()
        return airport_location


@dispatch(FlightRoute)
def save_route_options(option: FlightRoute):
    option.transportation.save()
    al_query = create_airport_location_query(option)
    existing_airport_locations = \
        {(al.airport_id, al.location_id): al for al in AirportLocation.objects.filter(al_query)}

    option.airport_location_0 = get_or_create_airport_location(option.airport_location_0, existing_airport_locations)
    option.airport_location_1 = get_or_create_airport_location(option.airport_location_1, existing_airport_locations)
    option.save()


@dispatch(DriveRoute)
def save_route_options(option: DriveRoute):
    option.transportation.save()
    option.save()


# TODO: what to do if route_options is empty
@transaction.atomic
def save_route(route: Route, route_options: List[RouteOption]):
    route.save()
    for opt in route_options:
        save_route_options(opt)
        route_option = RouteOption(content_object=opt, route=route)
        route_option.save()
    logging.info(f'finished saving route {route}')

