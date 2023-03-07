"""
Module for pulling NREL directly from the Open Energy Data Initiative
AWS S3 bucket.
https://data.openei.org/s3_viewer?bucket=oedi-data-lake
"""

import io
import boto3
from botocore import UNSIGNED
from botocore.client import Config
import pandas as pd

from sg2t.config import load_config


class API():
    def __init__(self,
                # source: str,
                 config_name = "config.ini",
                 config_key = "io.nrel.api"
                 ):
        """ API object initialization.

        Parameters
        ----------
        source: str
            Desired source of data to pull. Currently supports: ResStock, ComStock.

        config_name : str
            Name of configuration file in sg2t.config or cache directory to obtain API path settings.
        """
        self.source = None
        self.config_name = config_name
        self.config_key = config_key
        self.config = self.load_config(self.config_name, self.config_key)
        # API paths
        self.paths_amy_2018_v1 = {
            "end_use_loads": "https://oedi-data-lake.s3.amazonaws.com/"
                             "nrel-pds-building-stock/" \
                             "end-use-load-profiles-for-us-building-stock/",
            "resstock": "2022/resstock_amy2018_release_1/",
            "comstock": "2021/comstock_amy2018_release_1/"
        }
        # Climate zones
        self.climate_zones = ("cold", "hot-dry", "hot-humid", "marine", "mixed-dry",
                                "mixed-humid", "very-cold")
        # For commercial buildings, list does not change
        self.building_types = ("fullservicerestaurant", "quickservicerestaurant", "hospital",
                               "outpatient", "largehotel", "smallhotel", "largeoffice",
                               "mediumoffice", "smalloffice", "secondaryschool", "primaryschool",
                               "retailstripmall", "retailstandalone", "warehouse")
        # For residential homes
        self.home_types = ("mobile_home", "single-family_detached", "single-family_attached",
                             "multi-family_with_2_-_4_units", "multi-family_with_5plus_units")


    def load_config(self, config_name=None, key=None):
        """Load configuration.

        PARAMETERS
        ----------
        config_name : str
            Name of configuration file in sg2t.config, optional.

        key : str
            Key in config corresponding to this class, required if
            config_name is given.

        RETURNS
        -------
        config : dict
            Configuration dict, if any, otherwise None.
        """
        return load_config(config_name, key)

    # TODO: validate that options exist in class attribute sets
    def get_data_resstock_by_climatezone(self, climate, home_type, upgrade=0):
        """Pulls CSV"""
        climate_zone = climate.title()

        # for some reason "Very Cold" climate zone naming is set up differently
        if climate == "very-cold":
            climate = "very_cold"
            climate_zone = "Very%20Cold"

        # TODO: check if in cache, if not, pull from AWS
        # TODO: save tp cache after pulling
        filename = f"up{upgrade:02}-{climate}-{home_type}.csv"
        timeseries_aggregate_climate = f"timeseries_aggregates/" \
                                       f"by_building_america_climate_zone/" \
                                       f"upgrade={upgrade}/" \
                                       f"building_america_climate_zone={climate_zone}/" \
                                       f"{filename}"


        url =  self.paths_amy_2018_v1["end_use_loads"] +\
               self.paths_amy_2018_v1["resstock"] + \
               timeseries_aggregate_climate
        df = pd.read_csv(url, index_col=3)
        df.index = pd.to_datetime(df.index)
        return df

    def get_data_resstock_by_state(self, state, home_type, upgrade=0):
        """Pulls CSV"""
        state = state.upper()

        filename = f"up{upgrade:02}-{state.lower()}-{home_type}.csv"
        timeseries_aggregate_state = f"timeseries_aggregates/" \
                                     f"by_state/" \
                                     f"upgrade={upgrade}/" \
                                     f"state={state}/" \
                                     f"{filename}"


        url =  self.paths_amy_2018_v1["end_use_loads"] +\
               self.paths_amy_2018_v1["resstock"] + \
               timeseries_aggregate_state
        df = pd.read_csv(url, index_col=3)
        df.index = pd.to_datetime(df.index)
        return df

    def get_data_comstock_by_climatezone(self, climate, building_type):
        """Pulls CSV"""
        climate = climate.lower()

        if climate == "very-cold":
            raise("No ComStock data by Building America Climate Zone for 'Very-Cold'.")

        # for some reason "Very Cold" climate zone naming is set up differently
        if climate == "very-cold":
            climate = "very_cold"

        filename = f"{climate}-{building_type}.csv"
        timeseries_aggregate_climate = f"timeseries_aggregates/" \
                                       f"by_building_america_climate_zone/" \
                                       f"{filename}"

        url = self.paths_amy_2018_v1["end_use_loads"] +\
              self.paths_amy_2018_v1["comstock"] +\
              timeseries_aggregate_climate
        df = pd.read_csv(url, index_col=2)
        df.index = pd.to_datetime(df.index)
        return df

    def get_data_comstock_by_state(self, state, building_type):
        """Pulls CSV"""
        state = state.upper()

        filename = f"{state.lower()}-{building_type}.csv"
        timeseries_aggregate_climate = f"timeseries_aggregates/" \
                                       f"by_state/" \
                                       f"state={state}/" \
                                       f"{filename}"

        url = self.paths_amy_2018_v1["end_use_loads"] + \
              self.paths_amy_2018_v1["comstock"] + \
              timeseries_aggregate_climate
        df = pd.read_csv(url, index_col=2)
        df.index = pd.to_datetime(df.index)
        return df
