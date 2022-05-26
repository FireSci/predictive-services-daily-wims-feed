import asyncio
import logging
import typing as T

from wims_feed.constants import DATES
from wims_feed.io import get_station_data, get_station_list, sync_to_s3
from wims_feed.processors import process_data, write_data_to_file
from wims_feed.settings import Settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
loop = asyncio.get_event_loop()
settings = Settings()


async def worker(event, context):
    """Main worker"""

    BASE: str = "https://famprod.nwcg.gov/wims/xsql"

    # Get list of stns
    stns: T.List[T.Dict[str, T.Any]] = get_station_list(settings.station_path)

    logger.info(
        f"Processing {len(stns)} stations. This may take a few minutes!"
    )
    final_data = []
    for stn in stns:
        # Build request urls
        urls = [
            # Gets next seven day NFDRS16 forecast
            f"{BASE}/nfdrs.xsql?stn={stn['station_id']}&type=F&fmodel=16Y&start={DATES['nfdrs']['s'].strftime('%d-%b-%y')}&end={DATES['nfdrs']['e'].strftime('%d-%b-%y')}",
            # Gets past and Day 0 NFDRS obs
            f"{BASE}/nfdrs.xsql?stn={stn['station_id']}&type=N&fmodel=16Y&start={DATES['nfdrs_obs']['s'].strftime('%d-%b-%y')}&end={DATES['nfdrs_obs']['e'].strftime('%d-%b-%y')}&time={stn['rs']}",
            # Gets next seven day wx forecast
            f"{BASE}/pfcst.xsql?stn={stn['station_id']}&type=F&start={DATES['pfcst']['s'].strftime('%d-%b-%y')}&end={DATES['pfcst']['e'].strftime('%d-%b-%y')}",
            # Gets past and Day 0 wx obs
            f"{BASE}/obs.xsql?stn={stn['station_id']}&start={DATES['obs']['s'].strftime('%d-%b-%y')}&end={DATES['obs']['e'].strftime('%d-%b-%y')}&time={stn['rs']}",
        ]

        # Make requests to WIMS endpoints
        raw_data = await get_station_data(urls)

        # Process only the data we need
        processed_data = process_data(raw_data, stn)

        if not processed_data["headers"]:
            logger.warn(
                f"No data found for {stn['station_id']}. This station will not be written to file."
            )
        # Add to stn list
        final_data.append(processed_data)

    logger.info(
        f"Processing complete!. Writing data to file and making pretty."
    )

    # Write data to file
    write_data_to_file(final_data, f"/tmp/{settings.output_path}")

    logger.info(f"Uploading to S3!")
    # Upload file to S3
    with open(f"/tmp/{settings.output_path}", "rb") as f:
        msg = sync_to_s3(f)
    logger.info(f"{settings.output_path} was successfully synced!")
    return msg


def run(event, context):
    "Entry point when lambda is executed"
    return loop.run_until_complete(worker(event, context))
