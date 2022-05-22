import typing as T
from datetime import date, datetime, timedelta

import boto3

from wims_feed.constants import STN_LABELS
from wims_feed.helpers import enumerate_dates, wims_to_list
from wims_feed.settings import Settings

settings = Settings()
S3 = boto3.client("s3")


def process_data(stn_data: T.Dict[str, T.Dict], stn: T.Dict) -> T.Dict:
    """Process all of the required data for a station"""
    # Init dict of nine days
    dates: T.List[date] = enumerate_dates(
        (datetime.utcnow() - timedelta(days=1)).date(),
        (datetime.utcnow() + timedelta(days=9)).date(),
    )
    # This will be our final station object
    out_stn: T.Dict[str, T.List[T.Any]] = {
        d.strftime("%m/%d"): [] for d in dates
    }

    # Make sure data from endpoints are list, not dict. Happens when endpoint
    # response has only *one* ob/fcst
    stn_data = wims_to_list(stn_data)

    ###########################################################################
    #  Weather forecast processing                                            #
    ###########################################################################
    pfcst = stn_data["pfcst"]["row"]

    # Check and fill missing dates with -99
    if len(pfcst) != 9:
        missing_dts: T.List[str] = find_missing_dates(pfcst, "pfcst")
        for d in missing_dts:
            out_stn[d].extend(
                [
                    "-99",
                    "-99",
                    "-99",
                    "-99",
                    "-99",
                ]
            )
    # Fill found dates
    for day in pfcst:
        out_stn[day["fcst_dt"][:-5]].extend(
            [
                day["rh_max"],
                day["temp_min"],
                day["rh_min"],
                day["temp_max"],
                day["wind_sp"],
            ]
        )

    ###########################################################################
    # Weather obs processing                                                  #
    ###########################################################################
    obs: T.List[T.Dict] = stn_data["obs"]["row"]

    # Check and fill missing dates with -99
    if len(obs) != 2:
        missing_dts = find_missing_dates(obs, "obs")
        for d in missing_dts:
            out_stn[d].extend(
                [
                    "-99",
                    "-99",
                    "-99",
                    "-99",
                    "-99",
                ]
            )

    # Fill found dates
    for day in obs:
        out_stn[day["obs_dt"][:-5]].extend(
            [
                day["rh_max"],
                day["temp_min"],
                day["rh_min"],
                day["temp_max"],
                day["wind_sp"],
            ]
        )

    ###########################################################################
    # NFDRS obs processing                                                    #
    ###########################################################################
    nfdrs_obs: T.List[T.Dict] = stn_data["nfdrs_obs"]["row"]

    # Check and fill missing dates with -99
    if len(nfdrs_obs) != 2:
        missing_dts = find_missing_dates(nfdrs_obs, "nfdrs_obs")
        for d in missing_dts:
            out_stn[d].extend(["-99", "-99", "-99", "-99", "-99", "-99"])

    # Fill found dates
    for day in nfdrs_obs:
        out_stn[day["nfdr_dt"][:-5]].extend(
            [
                day["bi"],
                day["ec"],
                day["ic"],
                day["ten_hr"],
                day["hu_hr"],
                day["th_hr"],
            ]
        )

    ###########################################################################
    # NFDRS forecast processing                                               #
    ###########################################################################
    nfdrs_fcst: T.List[T.Dict] = stn_data["nfdrs"]["row"]

    # Check and fill missing dates with -99
    if len(nfdrs_fcst) != 9:
        missing_dts = find_missing_dates(nfdrs_fcst, "nfdrs")
        for d in missing_dts:
            out_stn[d].extend(["-99", "-99", "-99", "-99", "-99", "-99"])

    for day in nfdrs_fcst:
        out_stn[day["nfdr_dt"][:-5]].extend(
            [
                day["bi"],
                day["ec"],
                day["ic"],
                day["ten_hr"],
                day["hu_hr"],
                day["th_hr"],
            ]
        )

    # Write station headers (stn name, stn id, etc.)
    out_stn["headers"] = get_stn_headers(stn_data)

    return out_stn


def get_stn_headers(stn_data) -> T.List[str]:
    """Helper func to extract headers from first day of any endpoint result.
    Returns an empty list if we can't get any headers"""
    headers = []
    for k in stn_data:
        try:
            s = stn_data[k]["row"][0]
            today_dt = datetime.utcnow()
            headers = [
                f"*{s['sta_nm']}",
                s["sta_id"],
                str(round(float(s["latitude"]), 3)),
                str(round(float(s["longitude"]), 3)),
                today_dt.strftime("%Y%m%d"),
                today_dt.strftime("%H"),
            ]
            break
        # This just makes sure we write headers from at least 1 endpoint
        except KeyError:
            continue
    return headers


def find_missing_dates(data: T.List[T.Dict], d_type: str) -> T.List[str]:
    "Find the missing dates in the WIMS output. Spookyyyy"
    # Get a date range, inclusive ends
    # I hate this but the WIMS nfdrs call expects inconsistent dates so I can't
    # reuse the dates from constants.py
    if d_type in ["nfdrs", "pfcst"]:
        dates = enumerate_dates(
            (datetime.utcnow() + timedelta(days=1)),
            (datetime.utcnow() + timedelta(days=9)),
        )
    else:
        dates = enumerate_dates(
            (datetime.utcnow() - timedelta(days=1)),
            (datetime.utcnow()),
        )
    # Format to be like WIMS output
    date_strs = set([d.strftime("%m/%d") for d in dates])

    # Figure out which date key we need
    if d_type in ["nfdrs", "nfdrs_obs"]:
        data_date = "nfdr_dt"
    elif d_type == "obs":
        data_date = "obs_dt"
    else:
        data_date = "fcst_dt"

    # Get the dates from WIMS output
    wims_dates = set([day[data_date][:-5] for day in data])
    # Get the set difference
    return list(date_strs.difference(wims_dates))


def write_data_to_file(stns: T.List[T.Dict], file_path: str):
    with open(file_path, "w") as f:
        for stn in stns:
            # Write header row then remove from stn
            f.write("\t".join(stn["headers"]) + "\n")
            del stn["headers"]
            # Write date row
            sorted_dts = sorted(stn.keys())
            f.write(f"Fcst Dy\t" + "\t".join(sorted_dts) + "\n")
            # 11 rows for all the variables
            for i in range(11):
                row_vals = [stn[dt][i] for dt in sorted_dts]
                f.write(
                    f"{STN_LABELS['Fcst Dy'][i]}\t"
                    + "\t".join(row_vals)
                    + "\n"
                )
            f.write("\n")


# def write_data_to_file(stns: T.List[T.Dict], file_path: str):
#     """With justifying to resemble the original"""

#     with open(file_path, "w") as f:
#         for stn in stns:
#             # Write header row
#             f.write(
#                 f"{stn['headers'][0]:<20}{stn['headers'][1]:<8}{stn['headers'][2]:<8}{stn['headers'][3]:<8}{stn['headers'][4]:<10}{stn['headers'][5]:<5}\n"
#             )
#             del stn["headers"]
#             assert len(stn) == 9
#             # Write date row
#             sorted_dts = sorted(stn.keys())
#             f.write(f"Fcst Dy\t" + "\t".join(sorted_dts) + "\n")
#             # 11 rows for all the variables
#             for i in range(11):
#                 row_vals = [stn[dt][i] for dt in sorted_dts]
#                 f.write(
#                     f"{STN_LABELS['Fcst Dy'][i]}\t"
#                     + "\t".join(row_vals)
#                     + "\n"
#                 )
#             f.write("\n")
