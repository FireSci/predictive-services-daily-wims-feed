from datetime import date

import pytest

from wims_feed.helpers import enumerate_dates, rnd_wims, wims_to_list


def test_enumerate_dates():
    "Test date range creation"
    dates = enumerate_dates(date(2022, 1, 5), date(2022, 1, 7))
    assert isinstance(dates, list)
    assert all(isinstance(d, date) for d in dates)
    assert len(dates) == 3


def test_enumerate_dates_bad():
    "Test date range creation fails with string types"
    with pytest.raises(TypeError) as excinfo:
        dates = enumerate_dates("2022/1/5", "2022/1/7")
    assert (
        str(excinfo.value)
        == 'can only concatenate str (not "datetime.timedelta") to str'
    )


def test_wims_to_list_good():
    "Test where WIMS output is list of dates"
    dummy = {"nfdrs": {"row": [{"@num": "1", "sta_id": "20207"}]}}
    out = wims_to_list(dummy)
    assert isinstance(out, dict)
    assert isinstance(out["nfdrs"], dict)
    assert isinstance(out["nfdrs"]["row"], list)
    assert isinstance(out["nfdrs"]["row"][0], dict)


def test_wims_to_list_bad():
    "Test where WIMS output is a single dict of one date"
    dummy = {"nfdrs": {"row": {"@num": "1", "sta_id": "20207"}}}
    out = wims_to_list(dummy)
    assert isinstance(out, dict)
    assert isinstance(out["nfdrs"], dict)
    assert isinstance(out["nfdrs"]["row"], list)
    assert isinstance(out["nfdrs"]["row"][0], dict)


def test_rnd_wims():
    v = rnd_wims("98.99")
    assert v == "99"
    assert isinstance(v, str)
