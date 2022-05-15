###
# Simple script to convert all of the RAWS station IDs in provided file to a
# unique list of station IDs for use later

import json

import pandas as pd

# Drop GACC and PSA columns
df = pd.read_csv("SWA_stnlist_robust_05-14-22.csv").drop(
    ["NAME", "AGENCY", "PSA", "SHEFID"], axis=1
)

# This was for national file
# # Get only the unique values from all remaining columns. Ravel tells pandas to
# # flatten the columns into one series
# df = pd.unique(df[df.columns].values.ravel("k"))

# # Remove nan if it gets picked up from file, convert to ints to remove trailing
# # zeroes, then to string for easier use later in JSON
# df = df[~pd.isnull(df)].astype(int).astype(str)

# Dump to JSON, sorted for fun
with open("../station_list.json", "w") as outfile:
    json.dump(df.to_dict("records"), outfile)
