from pydantic import BaseSettings


class Settings(BaseSettings):
    """Variables and settings for the entire pipeline"""

    station_path: str = "station_list.json"
    output_path: str = "ndfd_predserv_fcst.txt"
    bucket_name: str = "predictive-services-open-data-us-west-2"
    # could make this env var if any semi-private emails need to be added
    notification_list: list = [
        "jclark754@gmail.com",
    ]
