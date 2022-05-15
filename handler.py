import json
import os
import logging
from re import S
import typing as T
from datetime import datetime

import boto3
import requests
import xmltodict

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

OUTPUT_PATH = "ndfd_predserv_fcst.txt"


def get_station_data(urls: T.Dict[str, str]) -> T.Dict[str, T.Dict]:
    """Given a list of URLs for a particular station, returns data from WIMS"""
    stn_data: T.Dict = {}
    for url in urls.values():
        response = requests.get(url)
        dict_data = xmltodict.parse(response.content)
        # Since we call nfdrs endpoint twice
        if "nfdrs" in stn_data and "nfdrs" in dict_data:
            dict_data["nfdrs_retro"] = dict_data.pop("nfdrs")
        stn_data = {**stn_data, **dict_data}
    return stn_data


def get_stn_headers(stn_data) -> T.List[str]:
    """Helper func to extract headers from first day of any endpoint result"""
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


def process_data(stn_data):
    out_stn = {}

    # Get headers (stn name, stn id, etc.)
    out_stn["headers"] = get_stn_headers(stn_data)

    try:
        pass
    except Exception as e:
        logger.info(e)
    return out_stn


def run(event, context):
    """Main lambda handler"""
    S3 = boto3.client("s3")
    start_date: str = datetime.utcnow().strftime("%d-%b-%y")

    # Load station data into memory
    with open("station_list.json") as json_file:
        stns: T.List[T.Dict[str, T.Any]] = json.load(json_file)

    for stn in stns:
        # Build request urls
        urls = {
            # Gets next seven day NFDRS16 forecast
            "nfdrs_forecast": f"https://famprod.nwcg.gov/wims/xsql/nfdrs.xsql?stn={stn['STNID']}&type=F&priority=&fmodel=16Y&ndays=7",
            # Gets past and Day 0 NFDRS obs
            "nfdrs_retro": f"https://famprod.nwcg.gov/wims/xsql/nfdrs.xsql?stn={stn['STNID']}&type=N&priority=&fmodel=16Y&ndays=1",
            # Gets next seven day wx forecast
            "wx_forecast": f"https://famprod.nwcg.gov/wims/xsql/pfcst.xsql?stn={stn['STNID']}&type=F&start={start_date}&ndays=7",
            # Gets past and Day 0 wx obs
            "wx_retro": f"https://famprod.nwcg.gov/wims/xsql/obs.xsql?stn={stn['STNID']}&ndays=1",
        }

        # Make requests
        stn_data = get_station_data(urls)

        # Process only the data we need
        stn_data = process_data(stn_data)

        # Write labels, this feels hacky
        stn_data["labels"] = {
            "Fcst Dy": [
                "Max RH (%)",
                "Min Temp (F)",
                "Min RH (%)",
                "Max Temp (F)",
                "WSpd (knt)",
                "BI",
                "ERC",
                "IC",
                "10-hr fuel (%)",
                "100-hr fuel (%)",
                "1000-hr fuel (%)",
            ]
        }
        print(stn_data)

        #    {
        #         "STNID": 20207,
        #         "RS": 13,
        #         "MP": 2,
        #         "MSGC": "16Y1P"
        #     },
        # Format station data

    # Write to txt file with tabs and new lines where needed
    with open(OUTPUT_PATH, "w") as f:
        f.write("test" + "\t" + "with tabs")

    # Save to S3, remove local file
    with open(OUTPUT_PATH, "rb") as f:
        S3.upload_fileobj(
            f,
            "predictive-services-open-data-us-west-2",
            OUTPUT_PATH,
        )
    os.remove(OUTPUT_PATH)
    return {"message": "WIMS data successfully written"}
