import typing as T
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory

import boto3

from wims_feed.settings import Settings

settings = Settings()
S3 = boto3.client("s3")


def process_data(stn_data: T.Dict[str, T.Dict], rs: int, mp: int, msgc: str):
    """Process all of the required data for a station"""
    out_stn = {}

    # Station headers (stn name, stn id, etc.)
    out_stn["headers"] = get_stn_headers(stn_data)

    ###########################################################################
    #  Weather forecast processing                                            #
    ###########################################################################
    pfcst: T.List[T.Dict] = stn_data["pfcst"]["row"]
    # TODO: error handling if not len 7
    assert len(pfcst) == 7
    for day in pfcst:
        # Remove year from date
        out_stn[day["fcst_dt"][:-5]] = [
            day["rh_max"],
            day["temp_min"],
            day["rh_min"],
            day["temp_max"],
            day["wind_sp"],
        ]

    ###########################################################################
    # Weather obs processing                                                  #
    ###########################################################################
    obs: T.List[T.Dict] = stn_data["obs"]["row"]
    obs = remove_non_rs_obs(obs, rs)
    # TODO: error handling if not len 2
    assert len(obs) == 2
    for day in obs:
        out_stn[day["obs_dt"][:-5]] = [
            day["rh_max"],
            day["temp_min"],
            day["rh_min"],
            day["temp_max"],
            day["wind_sp"],
        ]

    ###########################################################################
    # NFDRS obs processing                                                    #
    ###########################################################################
    # nfdrs_obs: T.List[T.Dict] = stn_data["nfdrs_retro"]["row"]
    # assert len(obs) == 2

    return out_stn


def get_stn_headers(stn_data) -> T.List[str]:
    """Helper func to extract headers from first day of any endpoint result.
    Returns an empty list if we can't get any headers"""
    headers = []
    for k in stn_data:
        try:
            s = stn_data["nfdrs"]["row"][0]
            today_dt = datetime.utcnow()
            headers = [
                f"*{s['sta_nm']}",
                s["sta_id"],
                s["latitude"],
                s["longitude"],
                today_dt.strftime("%Y%m%d"),
                today_dt.strftime("%H"),
            ]
            break
        # This just makes sure we write headers from at least 1 endpoint
        except KeyError:
            continue
    return headers


def remove_non_rs_obs(obs: T.List[T.Dict], rs: int) -> T.List[T.Dict]:
    """Itty bitty helper for removing obs that don't match our regularly
    scheduled time"""
    return [ob for ob in obs if ob["obs_tm"] == str(rs)]
