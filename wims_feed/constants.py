from datetime import datetime, timedelta

STN_LABELS = {
    "Fcst Dy": [
        "Max RH (%)",
        "Min Temp (F)",
        "Min RH (%)",
        "Max Temp (F)",
        "WSpd (knt)",
        "BI",
        "ERC",
        "IC",
        "10-hr fuel (%)",
        "100-hr fuel (%)",
        "1000-hr fuel (%)",
    ]
}


DATES = {
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
