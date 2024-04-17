"""
Module for pulling NREL directly from the Open Energy Data Initiative
AWS S3 bucket.
https://data.openei.org/s3_viewer?bucket=oedi-data-lake
"""

import io
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
            # 4/16/24 API breaking changes:
            # 2021 release has county breakdown
            # 2021 release does *not* take upgrades as input
            "resstock": "2021/resstock_amy2018_release_1/",
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
        # Geographic information
        self.df_geoinfo = self.get_geoinfo()


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

    def get_geoinfo(self):
        # This file is identical between ResStock and Comstock
        sector = "resstock"

        filename = f"spatial_tract_lookup_table.csv"
        spatial_tract_lookup_table = f"geographic_information/" \
                                       f"{filename}"

        url = self.paths_amy_2018_v1["end_use_loads"] + \
              self.paths_amy_2018_v1[sector] + \
              spatial_tract_lookup_table
        try:
            df = pd.read_csv(url, index_col=1) # nhgis_county_gisjoin as index
        except Exception as err:
            raise Exception(f"{err} (URL='{url}')")

        # Get county names
        df = df[df[f"{sector}_county_id"].str.contains("Not Applicable") == False]
        county_names = [x.split(" ")[1:-1] if x.endswith("County") else x.split(" ")[1:] for x in df[f"{sector}_county_id"]]
        county_names = [" ".join(x) for x in county_names]
        df["county_name"] = county_names

        return df

    def get_metadata(self, sector):
        filename = "metadata/metadata.parquet"

        url = self.paths_amy_2018_v1["end_use_loads"] + \
              self.paths_amy_2018_v1[sector] + \
              f"{filename}"

        try:
            df = pd.read_parquet(url)
        except Exception as err:
            raise Exception(f"{err} (URL='{url}')")

        # Only using these cols for now
        if sector.capitalize() == "Resstock":
            df = df[["in.county","in.geometry_building_type_recs","in.sqft"]]
        if sector.capitalize() == "Comstock":
            df = df[["in.county","in.building_type","in.sqft"]]
        return df

    def get_weather(self, county_gisjoin):
        # This file is identical between ResStock and Comstock
        # TODO double check this
        sector = "resstock"
        filename = f"{county_gisjoin.upper()}_2018.csv"

        url = self.paths_amy_2018_v1["end_use_loads"] + \
              self.paths_amy_2018_v1[sector] + \
              "weather/amy2018/" + \
              f"{filename}"

        try:
            df = pd.read_csv(url, index_col = ["date_time"])
        except Exception as err:
            raise Exception(f"{err} (URL='{url}')")

        return df

    def get_county_gisjoin_name(self, county_name=None, county_gisjoin=None):
        if county_name:
            return self.df_geoinfo[self.df_geoinfo["county_name"] == county_name.capitalize()].index[0]
        elif county_gisjoin:
            return self.df_geoinfo.iloc[self.df_geoinfo.index  == county_gisjoin.capitalize()]["county_name"].values[0]

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

    def get_data_resstock_by_climatezone_iecc(self, climate, home_type, upgrade=0):
        """Pulls CSV"""

        filename = f"up{upgrade:02}-{climate.lower()}-{home_type}.csv"
        timeseries_aggregate_climate = f"timeseries_aggregates/" \
                                       f"by_ashrae_iecc_climate_zone_2004/" \
                                       f"upgrade={upgrade}/" \
                                       f"ashrae_iecc_climate_zone_2004={climate.upper()}/" \
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
        try:
            df = pd.read_csv(url, index_col=3)
        except Exception as err:
            raise Exception(f"{err} (URL='{url}')")
        df.index = pd.to_datetime(df.index)
        return df

    def get_data_resstock_by_county(self, state, county_gisjoin, home_type, county_name=None):
        """Pulls CSV"""
        if not county_gisjoin and county_name:
            county_gisjoin = self.get_county_gisjoin_name(county_name=county_name)

        filename = f"{county_gisjoin.lower()}-{home_type.lower()}.csv"
        timeseries_aggregate_county = f"timeseries_aggregates/" \
                                     f"by_county/" \
                                     f"state={state.upper()}/" \
                                     f"{filename}"


        url =  self.paths_amy_2018_v1["end_use_loads"] +\
               self.paths_amy_2018_v1["resstock"] + \
               timeseries_aggregate_county
        try:
            df = pd.read_csv(url, index_col=2)
        except Exception as err:
            raise Exception(f"{err} (URL='{url}')")
        df.index = pd.to_datetime(df.index)
        return df

    # TODO: update comstock API calls (only state one is updated)
    def get_data_comstock_by_climatezone(self, climate, building_type, upgrade=0):
        """Pulls CSV"""
        climate = climate.lower()

        # for some reason "Very Cold" climate zone naming is set up differently
        if climate == "very-cold":
            climate = "very_cold"

        filename = f"up{upgrade:00}-{climate}-{building_type}.csv"
        timeseries_aggregate_climate = f"timeseries_aggregates/" \
                                       f"by_building_america_climate_zone/" \
                                       f"{filename}"

        url = self.paths_amy_2018_v1["end_use_loads"] +\
              self.paths_amy_2018_v1["comstock"] +\
              timeseries_aggregate_climate
        df = pd.read_csv(url, index_col=2)
        df.index = pd.to_datetime(df.index)
        return df

    def get_data_comstock_by_climatezone_iecc(self, climate, building_type, upgrade=0):
        """Pulls CSV"""
        
        filename = f"up{upgrade:00}-{climate.lower()}-{building_type}.csv"
        timeseries_aggregate_climate = f"timeseries_aggregates/" \
                                       f"by_ashrae_iecc_climate_zone_2004/" \
                                       f"{filename}"

        url = self.paths_amy_2018_v1["end_use_loads"] +\
              self.paths_amy_2018_v1["comstock"] +\
              timeseries_aggregate_climate

        df = pd.read_csv(url, index_col=2)
        df.index = pd.to_datetime(df.index)
        return df

    def get_data_comstock_by_state(self, state, building_type, upgrade=0):
        """Pulls CSV"""
        state = state.upper()

        filename = f"up{upgrade:02}-{state.lower()}-{building_type}.csv"
        timeseries_aggregate_state = f"timeseries_aggregates/" \
                                     f"by_state/" \
                                     f"upgrade={upgrade}/" \
                                     f"state={state}/" \
                                     f"{filename}"


        url =  self.paths_amy_2018_v1["end_use_loads"] +\
               self.paths_amy_2018_v1["comstock"] + \
               timeseries_aggregate_state
        df = pd.read_csv(url, index_col=3)
        df.index = pd.to_datetime(df.index)
        return df

    def get_data_comstock_by_county(self, state, county_gisjoin, building_type, county_name=None):
        """Pulls CSV"""
        if not county_gisjoin and county_name:
            county_gisjoin = self.get_county_gisjoin_name(county_name=county_name)

        filename = f"{county_gisjoin.lower()}-{building_type.lower()}.csv"
        timeseries_aggregate_county = f"timeseries_aggregates/" \
                                     f"by_county/" \
                                     f"state={state.upper()}/" \
                                     f"{filename}"

        url =  self.paths_amy_2018_v1["end_use_loads"] +\
               self.paths_amy_2018_v1["comstock"] + \
               timeseries_aggregate_county
        try:
            df = pd.read_csv(url, index_col=2)
        except Exception as err:
            raise Exception(f"{err} (URL='{url}')")
        df.index = pd.to_datetime(df.index)
        return df


