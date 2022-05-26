###
# Simple script to convert all of the RAWS station IDs in provided file to a
# unique list of station IDs for use later

import json

import pandas as pd

# Drop GACC and PSA columns
df = pd.read_csv("PS_NATIONAL_FINAL_20220524.csv").drop(
    ["station_name", "psa_name", "psa_code", "gaccid"], axis=1
)

# # Get only the unique values from all remaining columns. Ravel tells pandas to
# # flatten the columns into one series
df = df.drop_duplicates(subset=["station_id", "rs"])

# # Remove nan if it gets picked up from file, convert to ints to remove trailing
# # zeroes, then to string for easier use later in JSON
# df = df[~pd.isnull(df)].astype(int).astype(str)

# Dump to JSON, sorted for fun
with open("../station_list.json", "w") as outfile:
    json.dump(df.to_dict("records"), outfile)
print(f"{len(df)} stations written to json")
