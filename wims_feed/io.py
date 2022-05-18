import json
import requests
import typing as T

import xmltodict


def get_station_list(file_path: str) -> T.List[T.Dict[str, T.Any]]:
    """Loads station data in memory"""
    with open(file_path) as json_file:
        return json.load(json_file)


def get_station_data(urls: T.List[str]) -> T.Dict[str, T.Dict]:
    """Given a list of URLs for a particular station, returns data from WIMS.
    This should also return values for all endpoints even if its just None"""
    stn_data: T.Dict = {}
    for url in urls:
        response = requests.get(url)
        dict_data = xmltodict.parse(response.content)
        # Since we call nfdrs endpoint twice, this works because of order of
        # urls but will need to change if async implemented
        if "nfdrs" in stn_data and "nfdrs" in dict_data:
            dict_data["nfdrs_retro"] = dict_data.pop("nfdrs")
        stn_data = {**stn_data, **dict_data}
    return stn_data
