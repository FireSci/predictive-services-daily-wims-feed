import typing as T


class Config:
    """Pipeline configuration info"""

    BASE_URL: str = "https://famprod.nwcg.gov/wims/xsql"
    STATION_PATH: str = "station_list.json"
    OUTPUT_PATH: str = "ndfd_predserv_fcst.txt"
    BUCKET_NAME: str = "predictive-services-open-data-us-west-2"
    # could make this env var if any semi-private emails need to be added
    NOTIFICATION_LIST: T.List[str] = [
        "josh@firesci.io",
    ]
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
