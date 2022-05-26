import asyncio
import json
import logging
import typing as T

import aiohttp
import boto3
import xmltodict

from wims_feed.settings import Settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
settings = Settings()


def get_station_list(file_path: str) -> T.List[T.Dict[str, T.Any]]:
    """Loads station data in memory"""
    with open(file_path) as json_file:
        return json.load(json_file)


async def get_wims_data(url, session):
    """Async request to WIMs for a particular url"""
    try:
        async with session.get(url=url) as response:
            r = await response.read()
            return xmltodict.parse(r)

    except Exception as e:
        logger.error(f"Unable to get url {url} due to {e.__class__}.")


async def get_station_data(urls: T.List[str]) -> T.Dict[str, T.Dict]:
    """Given a list of URLs for a particular station, returns data from WIMS.
    This should return values for all endpoints even if its just None"""
    stn_data: T.Dict = {}
    # This is a context manager for establishing a session. Under the hood, there
    # is a lot of connection management stuff going on. Outta sight, outta mind
    async with aiohttp.ClientSession() as session:
        # This will be a 'batch' representing all four api responses for a stn
        url_resps: T.List[T.Dict] = await asyncio.gather(
            *[get_wims_data(url, session) for url in urls]
        )
    for resp in url_resps:
        if "nfdrs" in stn_data and "nfdrs" in resp:
            resp["nfdrs_obs"] = resp.pop("nfdrs")
        stn_data = {**stn_data, **resp}
    return stn_data


def sync_to_s3(file_path: str) -> T.Dict[str, str]:
    try:
        S3 = boto3.client("s3")
        S3.upload_fileobj(
            file_path, settings.bucket_name, settings.output_path
        )
        msg = {
            "status": "success",
            "desc": f"{settings.output_path} synced successfully!",
        }
    except Exception as e:
        msg = {
            "status": "failure",
            "desc": str(e),
        }
    return msg
