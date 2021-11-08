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


class GetRequestHandler:

    def __init__(self, **kwargs: Any):
        pass


def get(url: str, path: str, params: Dict[str, Any]) -> TrResponse:
    stringified_params = trenums.API_PARAMS_SEPARATOR.join(
        [f'{p_name}={p_value}' for (p_name, p_value) in params.items()])
    complete_url = f'{url}{path}{stringified_params}'
    response = requests.get(url=complete_url)
    return json.loads(response.text, object_hook=lambda d: TrResponse(**d))


def get_place_details(url: str, path: str, params: Dict[str, Any]) -> PlaceDetailsResponse:
    response0 = get(url, path, params)
    response:  PlaceDetailsResponse = response0
    return response


def main():
    resp = get()


if __name__ == '__main__':
    main()
