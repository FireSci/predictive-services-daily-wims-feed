import logging
import typing as T
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryFile

import boto3

from wims_feed.constants import STN_LABELS
from wims_feed.io import get_station_list, get_station_data
from wims_feed.processors import process_data
from wims_feed.settings import Settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

settings = Settings()


def run(event, context):
    """Main lambda handler"""
    S3 = boto3.client("s3")
    start_date: str = datetime.utcnow().strftime("%d-%b-%y")

    # Get list of stns
    stns: T.List[T.Dict[str, T.Any]] = get_station_list(settings.station_path)
    final_data = []

    for stn in stns:
        # Build request urls
        urls = [
            # Gets next seven day NFDRS16 forecast
            f"https://famprod.nwcg.gov/wims/xsql/nfdrs.xsql?stn={stn['STNID']}&type=F&priority=&fmodel=16Y&ndays=7",
            # Gets past and Day 0 NFDRS obs
            f"https://famprod.nwcg.gov/wims/xsql/nfdrs.xsql?stn={stn['STNID']}&type=N&priority=&fmodel=16Y&ndays=1",
            # Gets next seven day wx forecast
            f"https://famprod.nwcg.gov/wims/xsql/pfcst.xsql?stn={stn['STNID']}&type=F&start={start_date}&ndays=7",
            # Gets past and Day 0 wx obs
            f"https://famprod.nwcg.gov/wims/xsql/obs.xsql?stn={stn['STNID']}&ndays=1",
        ]

        # Make requests to WIMS endpoints
        raw_data = get_station_data(urls)

        # Checks if one endpoint failed. If so, log it and try next station
        # TODO: We enforce that a station has data for all urls
        if None in raw_data.values():
            # TODO: better error logging here
            continue

        # Process only the data we need
        processed_data = process_data(
            raw_data, stn["RS"], stn["MP"], stn["MSGC"]
        )

        final_data.append(processed_data)
        break

    g = open("/tmp/myfile.json", "w")
    g.write("test")
    g.close()

    with open("/tmp/myfile.json", "rb") as f:
        S3.upload_fileobj(
            f, "predictive-services-open-data-us-west-2", settings.output_path
        )

    return {"message": "WIMS data successfully written"}
