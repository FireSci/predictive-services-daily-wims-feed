from datetime import date

from wims_feed.helpers import enumerate_dates


def test_enumerate_dates():
    dates = enumerate_dates(date(2022, 1, 5), date(2022, 1, 7))
    assert isinstance(dates, list)
    assert all(isinstance(d, date) for d in dates)
    assert len(dates) == 3
