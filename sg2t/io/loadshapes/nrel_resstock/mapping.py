"""This module contains the mapping from NREL's ResStock laod TMY3 data to the standard sg2t data format.

Required columns for NREL
-------------------------
- Date
- Time
- Electricity Cooling
- Electricity Heating
- Fuel Oil Heating
- Natural Gas Heating
- Propane Heating
- Site Energy Total
- Electricity Total
- Fuel Oil Total
- Natural Gas Total
- Propane Total

Optional columns for NREL
-------------------------
- Any other data
"""
import os

from sg2t.utils.io import load_metadata


# Paths to metadata
package_dir =  os.environ["SG2T_HOME"]
metadata_file = f"{package_dir}/io/loadshapes/nrel_resstock/" + "resstock_nrel.json"

def get_map():
    # Raw columns from tmy3 data
    md = load_metadata(metadata_file)
    rs_cols = md["columns"]

    # Map required cols
    sg2t_cols = {
        "Datetime": "timestamp",
        "Electricity Cooling": "out.electricity.cooling.energy_consumption",
        "Electricity Heating": "out.electricity.heating.energy_consumption",
        "Fuel Oil Heating": "out.fuel_oil.heating.energy_consumption",
        "Natural Gas Heating": "out.natural_gas.heating.energy_consumption",
        "Propane Heating": "out.propane.heating.energy_consumption",
        "Site Energy Total": "out.site_energy.total.energy_consumption",
        "Electricity Total": "out.electricity.total.energy_consumption",
        "Fuel Oil Total": "out.fuel_oil.total.energy_consumption",
        "Natural Gas Total": "out.natural_gas.total.energy_consumption",
        "Propane Total": "out.propane.total.energy_consumption"
    }

    # Remove required/already added
    cols = list(rs_cols.keys())
    for key in list(sg2t_cols.keys()):
        cols.remove(sg2t_cols[key])

    # # Add the rest as is
    # for key in cols:
    #     # Renaming keys to adjust metadata
    #     sg2t_cols[rs_cols[key]] = key

    return sg2t_cols