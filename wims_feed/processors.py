import typing as T
from copy import deepcopy
from datetime import date, datetime, timedelta

from wims_feed.helpers import enumerate_dates, rnd_wims, wims_to_list
from wims_feed.settings import Config


def remove_extra_nfdrs(stn_data: T.Dict[str, T.Dict]) -> T.Dict:
    """Returns a copy of our stn data with extra data for all days removed. Some
    stns report values for multiple fuel models each day, even in cases where
    only the RS time is obtained (nfdrs_obs). Here we iterate through the days
    and remove any duplicates, taking only the first ob we find for that day,
    regardless of Y fuel model."""

    # Iterate through `stn_data` but do operations on `copy_dict` so we clone it
    copy_dict = deepcopy(stn_data)

    for ep in ["nfdrs", "nfdrs_obs"]:
        # Only do if we have a list of obs
        if stn_data[ep]["row"]:
            dt = None
            idxs = []
            # Find dates that match previous and grab respective indices
            for idx, ob in enumerate(stn_data[ep]["row"]):
                if ob["nfdr_dt"] == dt:
                    idxs.append(idx)
                dt = ob["nfdr_dt"]
            # If we have indices to delete, do it
            if idxs:
                # sort and reverse list to delete idxs without affecting others
                for idx in sorted(idxs, reverse=True):
                    del copy_dict[ep]["row"][idx]

    return copy_dict


def process_data(stn_data: T.Dict[str, T.Dict], stn: T.Dict) -> T.Dict:
    """Process all of the required data for a station"""
    # Init dict of eleven days
    # Note we only get data for 9 days but legacy WFAS format is 11 days so we
    # fill the last two dates with -99s so forecast systems don't break. Gross
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

    stn_data = remove_extra_nfdrs(stn_data)

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
                day.get("rh_max", "-99"),
                day.get("temp_min", "-99"),
                day.get("rh_min", "-99"),
                day.get("temp_max", "-99"),
                day.get("wind_sp", "-99"),
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
                day.get("rh_max", "-99"),
                day.get("temp_min", "-99"),
                day.get("rh_min", "-99"),
                day.get("temp_max", "-99"),
                day.get("wind_sp", "-99"),
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
                rnd_wims(day.get("bi", "-99")),
                rnd_wims(day.get("ec", "-99")),
                rnd_wims(day.get("ic", "-99")),
                rnd_wims(day.get("ten_hr", "-99")),
                rnd_wims(day.get("hu_hr", "-99")),
                rnd_wims(day.get("th_hr", "-99")),
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
                rnd_wims(day.get("bi", "-99")),
                rnd_wims(day.get("ec", "-99")),
                rnd_wims(day.get("ic", "-99")),
                rnd_wims(day.get("ten_hr", "-99")),
                rnd_wims(day.get("hu_hr", "-99")),
                rnd_wims(day.get("th_hr", "-99")),
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
        except (KeyError, IndexError):
            continue
    return headers


def find_missing_dates(data: T.List[T.Dict], d_type: str) -> T.List[str]:
    """Find the missing dates in the WIMS output. This will always be called on
    forecast wx and nfdrs endpoints since we only request 7 days of data but
    legacy ingest requires 9 forecast days. This will help us fill those last
    two days plus any missing dates.
    """
    # Get a date range, inclusive ends
    # Bummer to recreate date ranges here but the WIMS API date parameters are
    # different than the data. ~~GrAnDpA WiMs PrObz~~
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

    # Get the set difference (dates that are missing from WIMS)
    return list(date_strs.difference(wims_dates))


def write_data_to_file(stns: T.List[T.Dict], file_path: str):
    """With justifying to resemble the original"""
    with open(file_path, "w") as f:
        for stn in stns:
            try:
                # Write header row
                f.write(
                    f"{stn['headers'][0]:<20}{stn['headers'][1]:<8}{stn['headers'][2]:<8}{stn['headers'][3]:<9}{stn['headers'][4]:<10}{stn['headers'][5]:<5}\n"
                )
                del stn["headers"]

                # Write date row
                sorted_dts = sorted(stn.keys())
                f.write(
                    f"{'Fcst Dy':<20}"
                    + "".join(f"{x:<9}" for x in sorted_dts)
                    + "\n"
                )

                # Write variable rows
                # 11 rows for all the variables
                for i in range(11):
                    row_vals = [stn[dt][i] for dt in sorted_dts]
                    f.write(
                        f"{Config.STN_LABELS['Fcst Dy'][i]:<22}"
                        + "".join(f"{x:<9}" for x in row_vals)
                        + "\n"
                    )
                f.write("\n")

            # This happens when we don't have any station headers and all -99s
            except IndexError:
                continue
