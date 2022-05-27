import typing as T
from datetime import date, timedelta


def enumerate_dates(s: date, e: date) -> T.List[date]:
    """Returns a range of dates inclusive of both start and end."""
    dates = []
    while s <= e:
        dates.append(s)
        s += timedelta(days=1)
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
