from datetime import datetime

from wims_feed.constants import DATES, STN_LABELS


def test_stn_labels():
    """Make sure STN_LABELS constant doesn't change"""
    assert isinstance(STN_LABELS, dict)
    assert len(STN_LABELS) == 1
    assert "Fcst Dy" in STN_LABELS
    assert isinstance(STN_LABELS["Fcst Dy"], list)
    assert len(STN_LABELS["Fcst Dy"]) == 11


def test_dates():
    assert len(DATES) == 4
    for k in DATES:
        assert isinstance(DATES[k]["s"], datetime)
        assert isinstance(DATES[k]["e"], datetime)
