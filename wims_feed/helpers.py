import typing as T
from datetime import date, datetime, timedelta

from wims_feed.settings import Config


def _make_dates():
    """Simple helper to get the dates needed to build WIMS urls"""

    return {
        "nfdrs": {
            "s": datetime.utcnow(),
            "e": (datetime.utcnow() + timedelta(days=7)),
        },
        "nfdrs_obs": {
            "s": (datetime.utcnow() - timedelta(days=1)),
            "e": datetime.utcnow(),
        },
        "pfcst": {
            "s": (datetime.utcnow() + timedelta(days=1)),
            "e": (datetime.utcnow() + timedelta(days=7)),
        },
        "obs": {
            "s": (datetime.utcnow() - timedelta(days=1)),
            "e": datetime.utcnow(),
        },
    }


def build_urls(stn: T.Dict[str, str]):
    """Builds the four URLs needed to make calls to WIMS for a particular station"""

    DATES = _make_dates()

    return [
        # Gets next seven day NFDRS16 forecast
        f"{Config.BASE_URL}/nfdrs.xsql?stn={stn['station_id']}&type=F&fmodel=16Y&start={DATES['nfdrs']['s'].strftime('%d-%b-%y')}&end={DATES['nfdrs']['e'].strftime('%d-%b-%y')}",
        # Gets past and Day 0 NFDRS obs
        f"{Config.BASE_URL}/nfdrs.xsql?stn={stn['station_id']}&type=N&fmodel=16Y&start={DATES['nfdrs_obs']['s'].strftime('%d-%b-%y')}&end={DATES['nfdrs_obs']['e'].strftime('%d-%b-%y')}&time={stn['rs']}",
        # Gets next seven day wx forecast0
        f"{Config.BASE_URL}/pfcst.xsql?stn={stn['station_id']}&type=F&start={DATES['pfcst']['s'].strftime('%d-%b-%y')}&end={DATES['pfcst']['e'].strftime('%d-%b-%y')}",
        # Gets past and Day 0 wx obs
        f"{Config.BASE_URL}/obs.xsql?stn={stn['station_id']}&start={DATES['obs']['s'].strftime('%d-%b-%y')}&end={DATES['obs']['e'].strftime('%d-%b-%y')}&time={stn['rs']}",
    ]


def enumerate_dates(s: date, e: date) -> T.List[date]:
    """Returns a range of dates inclusive of both start and end."""

    dates = []
    while s <= e:
        dates.append(s)
        s += timedelta(days=1)
        s = date(s.year, s.month, s.day)
    return dates


def wims_to_list(
    stn_data: T.Dict[str, T.Dict],
) -> T.Dict[str, T.Dict[str, T.List[T.Dict[str, str]]]]:
    """In the case where only one observation is returned, WIMS will change
    the response type to dict instead of list. We need list."""

    for d in stn_data:
        # This is to handle those stns that might not report for an endpoint
        if stn_data[d] == None:
            stn_data[d] = {"row": []}

        if not isinstance(stn_data[d]["row"], list):
            stn_data[d]["row"] = [stn_data[d]["row"]]

    return stn_data


def rnd_wims(val: str) -> str:
    "Helper to round nfdrs values for matching legacy WIMS output."
    return str(round(float(val)))


def wims_str_to_date(val: str) -> date:
    """Helper to convert strings to date objects"""
    return datetime.strptime(val, "%m/%d/%Y").date()
