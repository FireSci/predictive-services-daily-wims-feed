from pydantic import BaseSettings


class Settings(BaseSettings):
    station_path: str = "station_list.json"
    output_path: str = "ndfd_predserv_fcst.txt"
    bucket_name: str = "predictive-services-open-data-us-west-2"
