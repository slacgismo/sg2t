"""This is the main class for working with weather data."""
import os
import json
import datetime
from math import sqrt

import numpy as np
import pandas as pd

from sg2t.config import load_config


# add here required desc of weather data based on schema


class Weather:
    """Weather class for working with weather data.
    At initialization:
        - load config, if any
        - filename = None

    Methods:
        - import_data (takes filename from user)
        - get_heat_index
        - plot
        - export
    """
    def __init__(self,
                 data,
                 config_name="config.ini",
                 config_key=None, #"weather.tmy3", # nothing in here yet
                 metadata_file=None, # new one? none for now
                 ):
        """ Weather object initialization.

        Parameters
        ----------
        data : pandas.DataFrame
            Dataframe contraining the weather data in sg2t format.
            Outputted from sg2t.io.

        config_name : str
            Name of configuration file in sg2t.config, optional.

        config_key : str
            Key in config corresponding to this class, required if
            config_name is given.

        metadata_file : str
            Full path to JSON file containing the metadata for this
             type of data.
        """
        self.data = data
        # self.config = self.load_config(config_name, config_key)
        # self.metadata_file = metadata_file
        # self.metadata = self.load_metadata(self.metadata_file)

    # TODO: move the two methods below to utils?
    def load_config(self, config_name=None, key=None):
        """Load TMY3 configuration
        Parameters
        ----------
        pathname : str
            Pathname of the configuration file to load
        Returns
        -------
        out : dict
            Configuration data loaded
        """
        if not config_name and not key:
            pass
        if not config_name:
            # Take default config file
            config_name = "config.ini"
        # Load config
        config = load_config(name=config_name)
        if key:
            try:
                return config[key]
            except KeyError:
                raise KeyError(f"No key defined in {config_name} for this data.")
        return None

    def load_metadata(self, filename=None):
        """Need to have this file """
        with open(filename) as f:
            # Return metadata dict
            return json.load(f)

    def plot(self, x_key, y_key):
        """Method for plotting the weather data"""
        self.data.plot( x_key, y_key)

    def get_hi(self, t, rh):
        """Method to calculate the heat index (HI) of weather data.

        Parameters
        ----------
        t : array
            Dry bulb temperature in degrees F.

        rh : array
            Relative humidity in %.

        Returns
        -------
        out : pandas.Series
            Returns the Series of HI and adds the Series to current data DF.
        """
        hi_array = np.vectorize(self.heat_index)(t, rh)
        # add to df and return series
        return hi_array

    @staticmethod
    def heat_index(t, rh):
        """Heat index (HI) calculation.
        HI is a non-linear combination of both dry bulb temperature
        and relative humidity [National Weather Service 2020].
        See https://www.wpc.ncep.noaa.gov/html/heatindex_equation.shtml
        for methodology.

        Parameters
        ----------
        t : float
            Dry bulb temperature in degrees F.

        rh : float
            Relative humidity in %.

        Returns
        -------
        out : float
            Heat index.
        """

        # use simple formula if HI<80 degF
        hi = 0.5 * (t + 61.0  + ((t - 68.0) * 1.2)  + (rh * 0.094))

        #for el in hi: need to do this for each pointcon
        if hi > 80:
            #  Rothfusz regression
            hi = -42.379 \
                 + 2.04901523 * t \
                 + 10.14333127 * rh \
                 - .22475541 * t * rh \
                 - .00683783 * t * t \
                 - .05481717 * rh * rh \
                 + .00122874 * t * t * rh \
                 + .00085282 * t * rh * rh \
                 - .00000199 * t * t * rh * rh

            # adjustments to regression
            if  rh < 13 and t > 80 and t < 112:
                adjustment = ((13 - rh) / 4) * sqrt((17 - abs(t - 95.)) / 17)
                hi -= adjustment

            elif  rh > 85 and t > 80 and t < 87:
                adjustment = ((rh - 85) / 10) * ((87 - t) / 5)
                hi += adjustment

        return hi

    @staticmethod
    def c_to_f(temp):
        """Degrees C to F conversion.

        Parameters
        ----------
        temp : float or array
            Temperature in degrees C.

        Returns
        -------
        out : float or array
            Temperature in degrees F.
        """
        return (temp * 9 / 5) + 32

