import json

import requests
from types import SimpleNamespace


def main():
    print('hello')

    URL = "https://maps.googleapis.com/maps/api/place/details/json?fields=name%2Crating%2Cformatted_phone_number%2Caddress_components&place_id=ChIJN1t_tDeuEmsRUsoyG83frY4&key=AIzaSyCiMV-wr0nGlRsg2Blz3jiPL6CKtXndJj4"

    # sending get request and saving the response as response object
    r = requests.get(url=URL)

    # extracting data in json format
    data = r.json()
    x = json.loads(r.text, object_hook=lambda d: SimpleNamespace(**d))

    print(data)


if __name__ == '__main__':
    main()
