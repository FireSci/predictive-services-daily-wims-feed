###
# Simple script to convert all of the RAWS station IDs in provided file to a
# unique list of station IDs for use later

import json

import pandas as pd

# Read csv, drop unnecessary columns
df = pd.read_csv("PS_NATIONAL_FINAL_20220524.csv").drop(
    ["station_name", "psa_name", "psa_code", "gaccid"], axis=1
)

# Drop duplicates
df = df.drop_duplicates(subset=["station_id", "rs"])

# Dump to JSON, sorted for fun
with open("../station_list.json", "w") as outfile:
    json.dump(df.to_dict("records"), outfile)

# 641 stns as of 6/2022
print(f"{len(df)} stations written to json")
