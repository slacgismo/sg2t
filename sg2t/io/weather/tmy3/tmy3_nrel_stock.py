"""Module for TMY3 data corresponding to NREL's
 ResStock and ComStock databases.
 Source: https://resstock.nrel.gov/datasets
"""

import os, sys
import datetime

import json
import pandas as pd

from sg2t.io.base import IOBase
from sg2t.config import load_config
from sg2t.io.schemas import weather_schema
from sg2t.utils.saving import NpEncoder as NpEncoder
from sg2t.io.weather.tmy3.mapping import get_map


package_dir = os.environ["SG2T_HOME"]
# TMY3 data cache
# Note this is only available locally
cache_dir = f"{package_dir}/weather/data/tmy3/nrel_stock/"
# Package cache
temp_dir =  os.environ["SG2T_CACHE"]


class TMY3Stock(IOBase):
    """TMY3 weather data file type implementation for basic i/o."""
    def __init__(self,
                 config_name="config.ini",
                 config_key="data.tmy3", # TODO: update/remove
                 metadata_file=package_dir+"/io/weather/tmy3/"+"tmy3_nrel_stock.json",
                 ):
        """ TMY3 object initialization.

        Parameters
        ----------
        config_name : str
            Name of configuration file in sg2t.config, optional.

        config_key : str
            Key in config corresponding to this class, required if
            config_name is given.

        metadata_file : str
            Full path to JSON file containing the metadata for this
             type of data.
        """
        super().__init__(config_name, config_key, metadata_file)

    def get_data(self, filename):
        """Get raw TMY3 data in DataFrame format.

        PARAMETERS
        ----------
        filename : str
            Filename, as "STATE-weather_station_name.tmy3".

        RETURNS
        -------
        out : pd.DataFrame
            DataFrame of data.
        """
        if not filename:
            raise FileNotFoundError(f"No data file provided.")

        self.data_filename = filename
        if not os.path.exists(self.data_filename):
            raise FileNotFoundError(f"File not found: {self.data_filename}")

        # Add source filename to metadata
        self.metadata["file"]["filename"] = self.data_filename

        # Data loaded into pandas df
        self.data = pd.read_csv(self.data_filename)

        # Returned data has to be a pd.DataFrame
        # This is the data as-is from the tmy3 files
        # Convert to standard format
        self._format_data()

        # Add to metadata.json
        self.metadata["columns"] = self.keys_map

        cols_list = list(self.keys_map.keys())
        units_list = [self._units(key) for key in cols_list]
        iterable = zip(cols_list, units_list)
        self.metadata["col_units"] = {key: value for (key, value) in iterable}

        # Rename file for now to avoid data loss
        # TODO: log saved json, or make saving optional
        new_name = self.metadata_file[:-5] + "_sg2t_io.json"
        outfile = open(new_name, "w")
        json.dump(self.metadata, outfile, cls=NpEncoder)
        outfile.close()

        return self.data

    def _format_data(self):
        """Changes the format of the loaded tmy3 data self.data to follow
        a standard format with standard column names. See `mapping.py`.

        This only reorders the columns, putting required ones first, and others
        next, and removes redundant/unused columns.
        """
        self.keys_map = get_map(stock=True)
        # Save original dataframe
        raw_data = self.data
        # Create new dataframe
        cols = list(self.keys_map.keys())
        data = pd.DataFrame(columns=cols)

        for key in list(self.keys_map.keys()):
            data[key] = raw_data[self.keys_map[key]]

        self.data = data
        self.data["Date"] = pd.to_datetime(self.data["Date"])
        self.data.set_index(["Date"])

    def export_data(self,
                    columns=None,
                    type="CSV",
                    filename=None):
        """Export data from pd.Daframe into a CSV file or into
        sg2t formatted DataFrame to pass onto sg2t opps.
        If saving to file, the file will be saved in the cache which
        can be accessed through os.environ["SG2T_CACHE"].

        PARAMETERS
        ----------
        columns : list of str
            List of columns to save/export from DataFrame.

        type : str
            Type of file to save data as. Currently only supports CSV.

        filename : str
            Name of output file. It will append a timestamp to that.

        RETURNS
        -------
        out : str
            Out filename and json metadata filename.
        """
        # need to update to formatted data
        filename = f"tmy3_{self.state.lower()}_{self.station_name.replace(' ', '_').lower()}"

        return self._export(columns=columns, filename=filename)

    def _units(self, key):
        """Method to get the unit corresponding to column
        from old mapping.

        PARAMETERS
        ----------
        key : str
            Column name.

        RETURNS
        -------
        unit : str
            String of unit.
        """
        data_key = self.keys_map[key]
        return self.metadata["col_units"][data_key]

    def units(self, key):
        """Method to get the unit corresponding to column
        from new mapping.

        PARAMETERS
        ----------
        key : str
            Column name.

        RETURNS
        -------
        unit : str
            String of unit.
        """
        return self.metadata["col_units"][key]

