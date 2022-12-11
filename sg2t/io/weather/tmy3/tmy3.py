"""Module for TMY3 data, adapted from  GridLAB-D"""
import os, sys
import datetime
import requests

import json
import pandas as pd

from sg2t.io.weather.base import IOBase
from sg2t.config import load_config
from sg2t.io.schemas import weather_schema
from sg2t.utils.saving import NpEncoder as NpEncoder


package_dir = os.environ["SG2T_HOME"]
# tmy3 data cache
cache_dir = f"{package_dir}/weather/data/tmy3/US/"
# package cache
temp_dir =  os.environ["SG2T_CACHE"]


class TMY3(IOBase):
    """TMY3 weather data file type implementation for basic i/o.

    This was written for the NREL TMY3 data, which can be found at
    https://github.com/slacgismo/gridlabd-weather
    """
    def __init__(self,
                 config_name="config.ini",
                 config_key="data.tmy3",
                 metadata_file=package_dir+"/io/weather/tmy3/"+"tmy3_nrel.json",
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

    def get_index(self):
        """Get list of weather stations from index of files.

        RETURNS
        -------
        out : list
            List of strings of the filenames as
            "STATE-weather_station_name.tmy3" sorted alphabetically.
        """
        index_filename = self.metadata["file"]["index_filename"]

        cache_file = f"{cache_dir}/{index_filename}"
        if os.path.exists(cache_file):
            with open(cache_file, "rt") as f:
                indices = f.read()

        return sorted(indices.strip().split("\n"))

    def get_dataframe(self, filename):
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
        metadata_rows = 1
        self.data = pd.read_csv(self.data_filename, skiprows=metadata_rows)

        # Parse metadata from TMY3
        self.metadata["station"] = {}
        metadata_keys = ["station_number","station_name","state",
                         "tzoffset","latitude","longitude","elevation"]
        info = pd.read_csv(self.data_filename, nrows=1, names=metadata_keys)

        for item in info.columns:
            setattr(self, item, info[item][0])
            self.metadata["station"][item] = info[item][0]

        # Add to metadata.json
        # Rename file for now to avoid data loss
        new_name = self.metadata_file[:-5] + "_sg2t_io.json"
        outfile = open(new_name, "w")
        json.dump(self.metadata, outfile, cls=NpEncoder)
        outfile.close()

    def create_sg2t_schema(self):
        """Create/adjust DataFrame to follow sg2t schema for use with
        other sg2t packages."""
        # TODO: finish implementation
        sg2t_export = {}

        columns = list(weather_schema["properties"].keys())
        required = weather_schema["required"]

        # tmy3 columns
        tmy_columns = list(self.metadata["columns"].keys())

        # Map TMY3 data to schema
        # Currently this is done by hand once here
        # TODO: automate and cross check with required keys?
        # date
        sg2t_export[columns[0]] = self.data[tmy_columns[1]]
        # time
        sg2t_export[columns[1]] = self.data[tmy_columns[2]]
        # drybulb
        sg2t_export[columns[2]] = self.data[tmy_columns[14]]
        # humidity
        sg2t_export[columns[3]] = self.data[tmy_columns[16]]
        # wind speed
        sg2t_export[columns[4]] = self.data[tmy_columns[19]]

        # make into DF, clean up, and make standard cols/formats/types based on schema
        # for now quick export below

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

        save_to_file : bool
            Whether to save to file. If false, it will only return the formatted DF.

        type : str
            Type of file to save data as. Currently only supports CSV.

        filename : str
            Name of output file. It will append a timestamp to that.

        RETURNS
        -------
        out : pd.DataFrame and json metadata filename
            DataFrame of data if it exists.
        """
        # need to update to formatted data
        if save_to_file:
            filename = f"tmy3_{self.state.lower()}_{self.station_name.replace(' ', '_').lower()}"

        self.export(columns=columns, save_to_file=save_to_file, filename=filename)

        # pass df
        return self.data
