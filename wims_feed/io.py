import asyncio
import json
import typing as T
from datetime import datetime
from io import BufferedReader

import aiohttp
import boto3
import xmltodict

from wims_feed.settings import Config


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


def sync_to_s3(
    file_path: BufferedReader, bucket: str, out_path: str
) -> T.Dict[str, T.Any]:
    """Upload final txt file to S3 and provide a helpful msg about sync status"""
    try:
        S3 = boto3.client("s3")
        S3.upload_fileobj(file_path, bucket, out_path)
        msg = {
            "status": "success",
            "desc": f"{out_path} synced successfully!",
        }
    except Exception as e:
        msg = {
            "status": "failure",
            "desc": str(e),
        }

    return msg


def send_email(email_body: T.Dict[str, T.Dict[str, str]]) -> None:
    """Send email report on pipeline status"""

    SES = boto3.client("ses", region_name="us-west-2")
    CHARSET = "UTF-8"
    HTML_EMAIL_CONTENT = f"""
        <html>
            <head></head>
            <h2>Daily WIMS Ingest Pipeline Notification</h2>
            <h3>Forecast File:</h3>
            <p>
            <b>STATUS:</b> {email_body['fcst_file']['status']}<br>
            <b>STATUS MESSAGE:</b> {email_body['fcst_file']['desc']}<br>
            <b>STATIONS PROCESSED:</b> {str(email_body['fcst_file']['num_stns'])}<br>
            <b>OUTPUT PATH:</b> <a href='https://predictive-services-open-data-us-west-2.s3.us-west-2.amazonaws.com/ndfd_predserv_fcst.txt' target='_blank'>https://predictive-services-open-data-us-west-2.s3.us-west-2.amazonaws.com/ndfd_predserv_fcst.txt</a>
            </p>
    """
    if email_body.get("error_file"):
        HTML_EMAIL_CONTENT_ERROR = f"""
            <h3>Errors File:</h3>
            <p>
            <b>STATUS:</b> {email_body['error_file']['status']}<br>
            <b>STATUS MESSAGE:</b> {email_body['error_file']['desc']} <br>
            <b>ERROR STATIONS:</b> {', '.join(str(stn) for stn in email_body['error_file']['error_stns'])}<br>
            <b>OUTPUT PATH:</b> <a href='https://predictive-services-open-data-us-west-2.s3.us-west-2.amazonaws.com/error_stns.txt' target='_blank'>https://predictive-services-open-data-us-west-2.s3.us-west-2.amazonaws.com/error_stns.txt</a>
            </p>
        """
        HTML_EMAIL_CONTENT += HTML_EMAIL_CONTENT_ERROR
    HTML_EMAIL_CONTENT += "</body></html>"

    response = SES.send_email(
        Destination={"ToAddresses": Config.NOTIFICATION_LIST},
        Message={
            "Body": {
                "Html": {
                    "Charset": CHARSET,
                    "Data": HTML_EMAIL_CONTENT,
                }
            },
            "Subject": {
                "Charset": CHARSET,
                "Data": f"{datetime.utcnow().strftime('%m-%d-%Y')} WIMS Ingest Pipeline Status",
            },
        },
        Source="josh@firesci.io",
    )
