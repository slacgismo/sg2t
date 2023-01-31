"""Module for ResStock Building data.
Data can be found at https://resstock.nrel.gov/datasets
and imported as parquet files.
TODO: add import options through API.
"""

import os, sys
import datetime

import json
import pandas as pd
import pyarrow.parquet as pq

from sg2t.io.base import IOBase
from sg2t.config import load_config
from sg2t.io.schemas import loadshape_schema
from sg2t.utils.saving import NpEncoder as NpEncoder
from sg2t.io.loadshapes.nrel_resstock.mapping import get_map

package_dir = os.environ["SG2T_HOME"]
# Package cache
temp_dir =  os.environ["SG2T_CACHE"]

class ResStock(IOBase):
    """Module for importing data from NREL's ResStock
     dataset into sg2t tools.
    """
    def __init__(self,
                 config_name="config.ini",
                 config_key="data.resstock",
                 metadata_file=None,
                 ):
        """ ResStock object initialization.

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
        self.weather_gisjoint = self.load_weather_location()

    def load_weather_location(self):
        # TODO: check that metadata exists
        if not self.metadata:
            return "None"
        try:
            gisj_metadata = self.metadata["file"]["GISJOINT ID"]
            return gisj_metadata
        except KeyError:
            return "None"

    def get_data(self, filename):
        """Import raw ResStock data in DataFrame format.

        PARAMETERS
        ----------
        filename : str
            Filename, as "ST_bldg_000000-0.parquet".

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

        # Read in raw data
        self.data = pq.read_pandas(filename).to_pandas()
        self.bldg_id = self.data.index[0]

        # Convert to standard format
        self._format_data()

        return self.data

    def _format_data(self):
        """Changes the format of the loaded tmy3 data self.data to follow
        a standard format with standard column names. See `mapping.py`.

        This only reorders the columns, putting required ones first, and others
        next, and removes redundant/unused columns.
        """
        self.keys_map = get_map()
        # Save original dataframe
        raw_data = self.data
        # Create new dataframe
        cols = list(self.keys_map.keys())
        data = pd.DataFrame(columns=cols)

        for key in list(self.keys_map.keys()):
            data[key] = raw_data[self.keys_map[key]]

        self.data = data
        self.data.insert(0, "Date", pd.to_datetime(self.data["Datetime"]).dt.date)
        self.data.insert(1, "Time", pd.to_datetime(self.data["Datetime"]).dt.time)
        self.data = self.data.drop(columns=["Datetime"])

    def export_data(self,
                columns=None,
                save_to_file=True,
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
        filename = f"resstock"

        return self.export(columns=columns, filename=filename)

    def units(self, key):
        """Method to get the unit corresponding to column key values.

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