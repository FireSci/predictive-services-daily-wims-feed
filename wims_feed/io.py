import asyncio
import json
import typing as T

import aiohttp
import boto3
import xmltodict

from wims_feed.settings import Settings

settings = Settings()


def get_station_list(file_path: str) -> T.List[T.Dict[str, T.Any]]:
    """Loads json stn data in memory from top-level dir"""
    with open(file_path) as json_file:
        return json.load(json_file)


async def get_wims_data(url, session):
    """Async request to WIMs for a particular url"""
    async with session.get(url=url) as response:
        r = await response.read()
        # Immediately get out of xml land
        return xmltodict.parse(r)


async def get_station_data(urls: T.List[str]) -> T.Dict[str, T.Dict]:
    """Given a list of URLs for a particular stn, returns data from WIMS.
    This should return values for all endpoints even if its just None"""
    stn_data: T.Dict = {}

    # Async obtain a 'batch' of stn data representing all four WIMS responses
    async with aiohttp.ClientSession() as session:
        url_resps: T.List[T.Dict] = await asyncio.gather(
            *[get_wims_data(url, session) for url in urls]
        )

    # Make sure we don't overwrite nfdrs forecast with obs (same key)
    for resp in url_resps:
        if "nfdrs" in stn_data and "nfdrs" in resp:
            resp["nfdrs_obs"] = resp.pop("nfdrs")
        # Unpack everything to stn_data dict
        stn_data = {**stn_data, **resp}

    return stn_data


def sync_to_s3(file_path: str) -> T.Dict[str, str]:
    """Upload final txt file to S3 and provide a helpful msg about sync status"""
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
