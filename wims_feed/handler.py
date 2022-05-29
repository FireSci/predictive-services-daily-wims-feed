import asyncio
import logging
import typing as T

from wims_feed.constants import DATES
from wims_feed.io import (
    get_station_data,
    get_station_list,
    send_email,
    sync_to_s3,
)
from wims_feed.processors import process_data, write_data_to_file
from wims_feed.settings import Settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
loop = asyncio.get_event_loop()
settings = Settings()


async def worker(event, context):
    """Main worker"""

    BASE: str = "https://famprod.nwcg.gov/wims/xsql"
    error_stns = []

    # Get list of stns
    stns: T.List[T.Dict[str, T.Any]] = get_station_list(settings.station_path)

    logger.info(f"Processing {len(stns)} stns. This will take ~4.5 minutes")
    final_data = []
    for stn in stns:
        # Build request urls
        urls = [
            # Gets next seven day NFDRS16 forecast
            f"{BASE}/nfdrs.xsql?stn={stn['station_id']}&type=F&fmodel=16Y&start={DATES['nfdrs']['s'].strftime('%d-%b-%y')}&end={DATES['nfdrs']['e'].strftime('%d-%b-%y')}",
            # Gets past and Day 0 NFDRS obs
            f"{BASE}/nfdrs.xsql?stn={stn['station_id']}&type=N&fmodel=16Y&start={DATES['nfdrs_obs']['s'].strftime('%d-%b-%y')}&end={DATES['nfdrs_obs']['e'].strftime('%d-%b-%y')}&time={stn['rs']}",
            # Gets next seven day wx forecast0
            f"{BASE}/pfcst.xsql?stn={stn['station_id']}&type=F&start={DATES['pfcst']['s'].strftime('%d-%b-%y')}&end={DATES['pfcst']['e'].strftime('%d-%b-%y')}",
            # Gets past and Day 0 wx obs
            f"{BASE}/obs.xsql?stn={stn['station_id']}&start={DATES['obs']['s'].strftime('%d-%b-%y')}&end={DATES['obs']['e'].strftime('%d-%b-%y')}&time={stn['rs']}",
        ]

        # Make requests to WIMS endpoints
        raw_data = await get_station_data(urls)

        # Process only the data we need
        processed_data = process_data(raw_data, stn)

        # This occurs when no data is returned from any wims endpoint
        if not processed_data["headers"]:
            logger.warn(
                f"No data found for {stn['station_id']}. This stn will not be written to file."
            )
            error_stns.append(stn["station_id"])
        # Add to stn list
        final_data.append(processed_data)

    # Write data to file
    logger.info(f"Processing complete!. Writing data to file...")
    write_data_to_file(final_data, f"/tmp/{settings.output_path}")

    email_body: T.Dict[str, T.Dict[str, str]] = {}
    # Upload file to S3
    logger.info(f"Uploading to S3...")
    with open(f"/tmp/{settings.output_path}", "rb") as f:
        msg = sync_to_s3(f, settings.bucket_name, settings.output_path)
        msg["num_stns"] = len(final_data)
        email_body["fcst_file"] = msg
    logger.info(f"{settings.output_path} was successfully synced!")

    # Write and upload errors to S3
    logger.info(f"Writing errors file...")
    if error_stns:
        error_path = "error_stns.txt"
        with open(f"/tmp/{error_path}", "w") as f:
            for stn in error_stns:
                f.write(f"{stn}\n")
        with open(f"/tmp/{error_path}", "rb") as f:
            msg = sync_to_s3(f, settings.bucket_name, error_path)
            msg["error_stns"] = error_stns
            email_body["error_file"] = msg

        logger.info(f"{error_path} was successfully synced!")

    # Send email notification
    send_email(email_body)

    logger.info("Pipeline complete! Check S3 for details.")


def run(event, context):
    "Entry point when lambda is executed"
    return loop.run_until_complete(worker(event, context))
