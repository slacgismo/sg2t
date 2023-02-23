"""This module contains the mapping from tmy3 data to the standard sg2t data format.

Required columns for weather
---------------------------
- Date
- Time
- Temperature (dry-bulb)
- Relative humidity

Optional columns for weather
---------------------------
- Any other data
"""
import os

from sg2t.utils.io import load_metadata


# Paths to metadata
package_dir =  os.environ["SG2T_HOME"]
metadata_path = f"{package_dir}/io/weather/tmy3/"

def get_map(stock=False):
    # Raw columns from tmy3 data
    if not stock:
        md = load_metadata(metadata_path + "tmy3_nrel.json")
    else:
        md = load_metadata(metadata_path + "tmy3_nrel_stock.json")
    tmy3_cols = md["columns"]

    if stock: # if using ResStock or ComStock TMY3, use all cols
        sg2t_cols = {}
        for k,v in zip(md["columns"].keys(), md["columns"].values()):
            sg2t_cols[v] = k

    else: # other NREL TMY3
        # Map required cols
        sg2t_cols = {
            "Date": "Date (MM/DD/YYYY)",
            "Time": "Time (HH:MM)",
            "Temperature": "Dry-bulb (C)",
            "Rel Humidity": "RHum (%)"
        }

    # Remove required/already added
    cols = list(tmy3_cols.keys())
    for key in list(sg2t_cols.keys()):
        cols.remove(sg2t_cols[key])

    # Add the rest as is
    for key in cols:
        # Renaming keys to remove units
        sg2t_cols[tmy3_cols[key]] = key

    return sg2t_cols