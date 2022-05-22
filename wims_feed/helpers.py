import typing as T
from datetime import date, timedelta


def enumerate_dates(s: date, e: date) -> T.List[date]:
    """Returns a range of dates inclusive of both start and end"""
    dates = []
    while s <= e:
        dates.append(s)
        s += timedelta(days=1)
    return dates


def wims_to_list(
    stn_data: T.Dict[str, T.Dict],
) -> T.Dict[str, T.Dict[str, T.List[T.Dict[str, str]]]]:
    """The WIMS endpoints can return dict instead of list for queries with
    results of len(1). We need everything to stay pretty as list"""
    for d in stn_data:
        if not isinstance(stn_data[d]["row"], list):
            stn_data[d]["row"] = [stn_data[d]["row"]]
    return stn_data
