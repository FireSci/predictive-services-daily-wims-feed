from datetime import datetime, timedelta

# Left most column labels for output file
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

# Dates for querying WIMS endpoints
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

CSV_HEADERS = {
    "FCST_DY",
    "STA_ID",
    "LATITUDE",
    "LONGITUDE",
    "ISSUE_DT",
    "ISSUE_TIME",
    "RH_MAX",
    "TEMP_MIN",
    "RH_MIN",
    "TEMP_MAX",
    "WIND_SP",
    "BI",
    "EC",
    "IC",
    "TEN_HR",
    "HU_HR",
    "TH_HR",
}
