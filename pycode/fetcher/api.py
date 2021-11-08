from typing import Any, Dict
import trenums
import requests
import logging
from types import SimpleNamespace
from abc import ABC
import json


class TrResponse(ABC, SimpleNamespace):
    pass


class PlaceDetailsResponse(TrResponse):
    pass


class FindPlaceResponse(TrResponse):
    pass


def get(url: str, path: str, params: Dict[str, Any], response_type) -> TrResponse:
    complete_url = f'{url}{path}'
    response = requests.get(url=complete_url, params=params)
    return json.loads(response.text, object_hook=lambda d: response_type(**d)).result


def get_place_details(url: str, path: str, params: Dict[str, Any]) -> PlaceDetailsResponse:
    stringified_fields = ','.join(params['fields'])
    params['fields'] = stringified_fields
    response = get(url, path, params, PlaceDetailsResponse)
    return response


def main():
    fields = ['name', 'rating', 'formatted_phone_number', 'address_components']
    params = {'place_id': 'ChIJN1t_tDeuEmsRUsoyG83frY4', 'fields': fields, 'key': 'AIzaSyCiMV-wr0nGlRsg2Blz3jiPL6CKtXndJj4'}
    resp = get_place_details(trenums.GOOGLE_MAPS_API_URL, trenums.PLACE_DETAILS_PATH, params)


if __name__ == '__main__':
    main()
