from typing import Dict, List
from functools import reduce
import logging
from django.db.models import Q

from trippin.tr_db import Route, FlightRoute, AirportLocation, DriveRoute, RouteContent, BaseRoute, LocationContent, GeneralLocation

logging.basicConfig(level=logging.INFO)
from django.db import transaction
from trippin.pycode.tr_utils import TR_ID
from multipledispatch import dispatch
from .data_classes import *


def create_airport_location_query(flight_route_data: FlightRouteData):
    airport_location_queries = [Q(airport_id=al.airport.id, location_id=al.location.id) for al in
                                [flight_route_data.airport_location_0, flight_route_data.airport_location_1]]
    return reduce(lambda alq0, alq1: alq0 | alq1, airport_location_queries)


# TODO: fix type hint
def get_or_create_airport_location(airport_location_data: AirportLocationData,
                                   existing_airport_locations) -> AirportLocation:
    # existing_airport_locations: Dict[(TR_ID, TR_ID), AirportLocation]) -> AirportLocation:
    existing_airport_location = existing_airport_locations.get(
        (airport_location_data.airport.id, airport_location_data.location.id), None)
    if existing_airport_location:
        return existing_airport_location
    else:
        airport_location_data.transportation.save()
        location_content = LocationContent(content_object=airport_location_data.location)
        location_content.save()
        airport_location = AirportLocation(airport=airport_location_data.airport, location=location_content,
                                           transportation=airport_location_data.transportation)
        airport_location.save()
        return airport_location


@dispatch(FlightRouteData)
def save_route_options(option_data: FlightRouteData) -> FlightRoute:
    option_data.transportation.save()
    al_query = create_airport_location_query(option_data)
    existing_airport_locations = \
        {(al.airport_id, al.location_id): al for al in AirportLocation.objects.filter(al_query)}

    airport_location_0 = get_or_create_airport_location(option_data.airport_location_0, existing_airport_locations)
    airport_location_1 = get_or_create_airport_location(option_data.airport_location_1, existing_airport_locations)
    flight_option = FlightRoute(airport_location_0=airport_location_0, airport_location_1=airport_location_1,)
    flight_option.save()
    return flight_option


@dispatch(DriveRouteData)
def save_route_options(option: DriveRouteData) -> DriveRoute:
    option.transportation.save()
    drive_option = DriveRoute(transportation=option.transportation)
    drive_option.save()
    return drive_option


# TODO: what to do if route_options is empty
@transaction.atomic
def save_route(route_data: RouteData, route_options_data: List[BaseRouteData]):
    location_content_0 = LocationContent(content_object=route_data.location_0)
    location_content_1 = LocationContent(content_object=route_data.location_1)
    location_content_0.save()
    location_content_1.save()
    route = Route(location_0=location_content_0, location_1=location_content_1)
    route.save()
    for opt_data in route_options_data:
        opt = save_route_options(opt_data)
        route_option = RouteContent(content_object=opt, route=route)
        route_option.save()
    logging.info(f'finished saving route {route}')

