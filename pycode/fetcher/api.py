from typing import Any, Dict
import requests
from types import SimpleNamespace
from abc import ABC
import json
import os


class TrResponse(ABC, SimpleNamespace):
    pass


class PlaceDetailsResponse(TrResponse):
    pass


class FindPlaceResponse(TrResponse):
    pass


def get(url: str, path: str, params: Dict[str, Any], response_type) -> TrResponse:
    complete_url = f'{url}{path}'
    params['key'] = os.environ['API_KEY']
    response = requests.get(url=complete_url, params=params)
    return json.loads(response.text, object_hook=lambda d: response_type(**d))


def place_details(place_id: str) -> PlaceDetailsResponse:
    params = {'place_id': place_id, 'fields': ','.join(trenums.PLACE_DETAILS_FIELDS)}
    response = get(trenums.GOOGLE_MAPS_API_URL, trenums.PLACE_DETAILS_PATH, params, PlaceDetailsResponse).result
    return response


def find_place(name: str) -> FindPlaceResponse:
    params = {'input': name, 'fields': ','.join(trenums.FIND_PLACE_FIELDS), 'inputtype': 'textquery'}
    response = get(trenums.GOOGLE_MAPS_API_URL, trenums.FIND_PLACE_PATH, params, FindPlaceResponse)
    return response
