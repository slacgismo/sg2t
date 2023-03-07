"""This is the main class for working with weather data."""
import os
import datetime
from math import sqrt

import numpy as np
import pandas as pd
import json

from sg2t.config import load_config
from sg2t.utils.io import load_metadata


# add here required desc of weather data based on schema


class Weather:
    """Weather class for working with weather data."""
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
        self.config = self.load_config(config_name, config_key)
        self.metadata_file = metadata_file
        self.metadata = self.load_metadata(self.metadata_file)

    def load_config(self, config_name=None, key=None):
        """Load weather configuration.

        Parameters
        ----------
        pathname : str
            Pathname of the configuration file to load

        Returns
        -------
        out : dict
            Configuration data loaded
        """
        return load_config(config_name, key)

    def load_metadata(self, filename=None):
        """Load metadata of dataset.

        PARAMETERS
        ----------
        filename : str
            Full path to metadata file.

        RETURNS
        -------
        metadata : dict
            Metadata dict, if any, otherwise a dict w/ no values
             with keys based on the metadata schema.
        """
        return load_metadata(filename)

    def plot(self, x_key, y_key, linewidth=0, marker=".", **kwargs):
        """Method for plotting the weather data.
        Uses pd.DataFrame.plot() method.

        PARAMETERS
        ----------
        x_key : str
            Column name for x-axis data.

        y_key : str
            Column name for y-axis data.
        """
        if x_key in self.metadata["col_units"].keys():
            x_units = "(" + self.metadata["col_units"][x_key] + ")"  if \
                self.metadata["col_units"][x_key] != "None" else\
                ""
        else:
            x_units = ""
        x_label = f"{x_key} {x_units}"

        if isinstance(y_key, list) and len(y_key) > 1:
            # if only plotting more than one col
            y_units = ""  # does not add unit info if plotting more than 1
            y_label = None
        else:
            # if plotting one col
            if y_key in self.metadata["col_units"].keys():
                y_units = "(" + self.metadata["col_units"][y_key] + ")" if \
                    self.metadata["col_units"][y_key] != "None" else ""
                y_label = fr"{y_key} {y_units}"
            else:
                # if no unit info
                y_units = ""
                y_label = fr"{y_key} {y_units}"

        self.data.plot( x_key,
                        y_key,
                        xlabel=x_label,
                        ylabel=y_label,
                        linewidth=linewidth,
                        marker=marker,
                        **kwargs)

    def between_dates(self, start, end, columns=None):
        """Method to get data between two specific dates.
         Includes both end-points in the result *if* they
         are in the index. Columns optional otherwise all
         are returned.

        Parameters
        ----------
        start : str
            Start date in form 'YYYY-M-D'.

        end : str
            End date in form 'YYYY-M-D'.

        columns : list of str
            List of columns to include. Optional.

        Returns
        -------
        out : pandas.DataFrame
            Returns the subset of the original DF that
             falls between start and end.
        """
        # check that date col is datetime object?
        # or do validation at instantiation?
        l_cond = self.data['Date'] > start
        r_cond = self.data['Date'] <= end
        data_cond = self.data[(l_cond) & (r_cond)]

        if columns:
            data_cond = data_cond[columns]

        return data_cond


    def get_hi(self):
        """Method to calculate the heat index (HI) of weather data.

        Parameters
        ----------
        t : array
            Dry bulb temperature in degrees C or F.

        rh : array
            Relative humidity in %.

        Returns
        -------
        out : pandas.Series
            Returns the Series of HI and adds the Series to current data DF.
        """
        # Check both exist
        if "Temperature" not in self.data.columns or \
                "Rel Humidity" not in self.data.columns:
            raise("Missing Temperature or Rel Humidity columns for calculating HI.")

        # Data
        temp = self.data["Temperature"]
        rh = self.data["Rel Humidity"]

        # Check metadata for units and convert if necessary
        if "Temperature" in self.metadata["col_units"].keys():
            if self.metadata["col_units"]["Temperature"] == "degrees C":
                temp = self.c_to_f(temp)
        else:
            print("No metadata to check units. Make sure Temperature is in degrees F. " +
                  "To convert, use Weather.c_to_f method.")

        # Calculate HI
        hi_array_f = np.vectorize(self.heat_index)(temp, rh)
        hi_array_c = self.f_to_c(hi_array_f)

        # Add to df and metadata and return series
        # Store in CELCIUS
        self.data["Heat Index"] = hi_array_c
        if self.metadata:
            self.metadata["columns"]["Heat Index"] = "heat index"
            self.metadata["col_units"]["Heat Index"] = "degrees C"
            self.metadata["col_types"]["Heat Index"] = "float"

        return self.data["Heat Index"]

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

    @staticmethod
    def f_to_c(temp):
        """Degrees F to C conversion.

        Parameters
        ----------
        temp : float or array
            Temperature in degrees F.

        Returns
        -------
        out : float or array
            Temperature in degrees C.
        """
        return (temp - 32) * 5 / 9

