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
metadata_file = f"{package_dir}/io/weather/tmy3/" + "tmy3_nrel.json"

def get_map():
    # Raw columns from tmy3 data
    md = load_metadata(metadata_file)
    tmy3_cols = md["columns"]

    # Map required cols
    sg2t_cols = {
        "Date" : "Date (MM/DD/YYYY)",
        "Time" : "Time (HH:MM)",
        "Temperature" : "Dry-bulb (C)",
        "Rel Humidity" : "RHum (%)"
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