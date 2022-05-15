import json
import os
import logging
from datetime import date

import boto3

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Required WIMS params
#   stn=??
#   start=dd-mon-yy
#   end=dd-mon-yy
#   ndays=??
#   * note leaving start and end blank will return most recent x days

OUTPUT_PATH = "ndfd_predserv_fcst.txt"


def get_station_data(stn_id: str):
    pass


def run(event, context):
    S3 = boto3.client("s3")

    # start_date = date.today().strftime("%d-%b-%y")

    # with open("station_list.json") as json_file:
    #     stn_ids = json.load(json_file)["stations"]

    # for stn_id in stn_ids:
    #     # Note, sorting applies to wx_retro,
    #     urls = {
    #         "nfdrs_forecast": f"https://famprod.nwcg.gov/wims/xsql/nfdrs.xsql?stn={stn_id}&type=F&priority=&fmodel=16Y&sort=asc&ndays=7",
    #         "nfdrs_retro": f"https://famprod.nwcg.gov/wims/xsql/nfdrs.xsql?stn={stn_id}&type=N&priority=&fmodel=16Y&ndays=1&sort=asc",
    #         "wx_forecast": f"https://famprod.nwcg.gov/wims/xsql/pfcst.xsql?stn={stn_id}&type=F&start={start_date}&ndays=7&sort=asc",
    #         "wx_retro": f"https://famprod.nwcg.gov/wims/xsql/obs.xsql?stn={stn_id}&type=O&ndays=1&sort=asc",
    #     }

    #     break

    # Get all data for stations

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
