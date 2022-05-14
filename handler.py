import json
import logging
from datetime import date


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Required WIMS params
#   stn=??
#   start=dd-mon-yy
#   end=dd-mon-yy
#   ndays=??
#   * note leaving start and end blank will return most recent x days


def get_station_data(stn_id: str):
    pass


def run(event, context):
    start_date = date.today().strftime("%d-%b-%y")

    with open("station_list.json") as json_file:
        stn_ids = json.load(json_file)["stations"]

    for stn_id in stn_ids:
        urls = {
            "nfdrs_forecast": f"https://famprod.nwcg.gov/wims/xsql/nfdrs.xsql?stn={stn_id}&type=F&priority=&fmodel=16Y&sort=asc&ndays=7",
            "nfdrs_retro": f"https://famprod.nwcg.gov/wims/xsql/nfdrs.xsql?stn={stn_id}&type=N&priority=&fmodel=16Y&ndays=1&sort=asc",
            "wx_forecast": f"https://famprod.nwcg.gov/wims/xsql/pfcst.xsql?stn={stn_id}&type=F&start={start_date}&ndays=7&sort=asc",
            "wx_retro": f"https://famprod.nwcg.gov/wims/xsql/obs.xsql?stn={stn_id}&type=O&ndays=1&sort=asc",
        }

        break
