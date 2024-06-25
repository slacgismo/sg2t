"""Module for ResStock and ComStock Building data.
Data can be found at https://resstock.nrel.gov/datasets
"""

import os, sys
import datetime

import json
import pandas as pd

from sg2t.io.base import IOBase
from sg2t.io.schemas import loadshape_schema
from sg2t.utils.saving import NpEncoder as NpEncoder
from sg2t.config import load_config
from sg2t.io.loadshapes.nrel.naming import CLIMATE_ZONES_BA, CLIMATE_ZONES_IECC, HOME_TYPES, BUILDING_TYPES, NREL_COL_MAPPING


package_dir = os.environ["SG2T_HOME"]
# Package cache
temp_dir =  os.environ["SG2T_CACHE"]

class BuildStock(IOBase):
    """Class for importing data from NREL's ResStock and ComStock
     dataset into sg2t tools.
    """
    def __init__(self,
                 data,
                 metadata,
                 api=None
                 ):
        """ ResStock object initialization.
        # TODO: update docstrings
        """
        self.raw_data = data
        self.data = self._format_data()
        self.data_normalized = None
        self.metadata = metadata
        self.api = api
        self._validate_metadata()

    def _format_data(self):

        self.data = self.raw_data.copy()

        # adjust col names to same standard between resstock and comstock
        self.data.rename(columns=
        {
            "in.county": "county",
            "in.geometry_building_type_recs": "building_type", # resstock
            "in.building_type": "building_type", # comstock
        },
            inplace=True
        )
        # rename the rest of the cols # TODO: do i need this
        # self.data.rename(columns=NREL_COL_MAPPING, inplace = True)
        # self.data = self.data[self.data.columns.intersection([*NREL_COL_MAPPING.values()])]

        return self.data

    def _validate_metadata(self):
        # TODO: do I actually need this
        keys_set = set(self.metadata.keys())
        try:
            assert keys_set == {'sector', 'state', 'building_type'}  or \
                   keys_set == {'sector', 'state', 'county_name', 'building_type'}  or \
                   keys_set == {'sector', 'climate', 'building_type'}

        except AssertionError:
            print("Please specify the sector in the metadata, and: \n \
                  - the state, or \n \
                  - the state and county, or \n \
                  - the climate")

    def normalize_by_sqft(self):
        """ Normalize county-level data by square footage
        and return energy/SF for each building type
        """
        if "county" not in self.data.columns:
            raise Exception("Must have county level data specified to call this method.")

        # create API object
        # TODO: maybe change how this is implemented
        # TODO: maybe can pass metadata if cached to speed it up
        self.api = self.api if self.api else API()

        # TODO: speed up (takes 17s)
        # get SF per build type
        meta = self.api.get_metadata(self.metadata["sector"])
        area = meta.groupby(["county", "building_type"]).sum()
        area.columns = ["floor_area[sf]"]
        area.reset_index(inplace=True)

        # get county puma
        puma = self.api.get_county_gisjoin_name(self.metadata["county_name"], self.metadata["state"])

        # sort SF by county and building type
        area = area[area["county"] == puma] # TODO: do i need to do this or is it always one county?
        area.set_index(["county", "building_type"], inplace=True)

        # join data with SF metadata
        self.data_normalized = self.data.copy()
        self.data_normalized.reset_index(inplace=True)
        self.data_normalized.set_index(["county", "building_type"], inplace=True)
        self.data_normalized = self.data_normalized.join(area)

        dt = 0.25 # same for ResStock and ComStock
        columns = []
        for column in self.data_normalized.columns:
            if column.endswith("consumption"):
                self.data_normalized[column] = self.data_normalized[column] / self.data_normalized["floor_area[sf]"] / dt
            columns.append(column.replace("consumption", "consumption[kW/sf]"))

        self.data_normalized.columns = columns
        self.data_normalized.drop("floor_area[sf]", axis=1, inplace=True)
        self.data_normalized.reset_index(inplace=True)
        self.data_normalized.set_index("timestamp", inplace=True)
        self.data_normalized.sort_index(inplace=True)

        return self.data_normalized

    # def export_data(self,
    #             columns=None,
    #             save_to_file=True,
    #             type="CSV",
    #             filename=None):
    #     """Export data from pd.Daframe into a CSV file or into
    #     sg2t formatted DataFrame to pass onto sg2t opps.
    #     If saving to file, the file will be saved in the cache which
    #     can be accessed through os.environ["SG2T_CACHE"].
    #     PARAMETERS
    #     ----------
    #     columns : list of str
    #         List of columns to save/export from DataFrame.
    #
    #     type : str
    #         Type of file to save data as. Currently only supports CSV.
    #
    #     filename : str
    #         Name of output file. It will append a timestamp to that.
    #
    #     RETURNS
    #     -------
    #     out : str
    #         Out filename and json metadata filename.
    #     """
    #     filename = f"resstock"
    #
    #     return self._export(columns=columns, filename=filename)
    #
    # def _units(self, key):
    #     """Method to get the unit corresponding to column
    #     from old mapping.
    #
    #     PARAMETERS
    #     ----------
    #     key : str
    #         Column name.
    #
    #     RETURNS
    #     -------
    #     unit : str
    #         String of unit.
    #     """
    #     data_key = self.keys_map[key]
    #     return self.metadata["col_units"][data_key]
    #
    # def units(self, key):
    #     """Method to get the unit corresponding to column
    #     from new mapping.
    #
    #     PARAMETERS
    #     ----------
    #     key : str
    #         Column name.
    #
    #     RETURNS
    #     -------
    #     unit : str
    #         String of unit.
    #     """
    #     return self.metadata["col_units"][key]


class API:
    """
    Class for pulling NREL directly from the Open Energy Data Initiative
    AWS S# bucket.
    https://data.openei.org/submissions/4520
    """
    def __init__(self):
        """ API object initialization
        """
        # API paths
        # 2021 release has county breakdown
        # 2021 release does *not* take upgrades as input
        self.release_year = 2021 # 2021 to 2024
        self.amy = 2018 # some have 2012 available
        self.release_number = 1 # 1, 1.1 or 2
        self.paths_amy_2018_v1 = {
            "end_use_loads": "https://oedi-data-lake.s3.amazonaws.com/"
                             "nrel-pds-building-stock/" \
                             "end-use-load-profiles-for-us-building-stock/",
            "resstock": f"{self.release_year}/resstock_amy{self.amy}_release_{self.release_number}/",
            "comstock": f"{self.release_year}/comstock_amy{self.amy}_release_{self.release_number}/"
        }
        # Climate zones
        self.climate_zones_ba = CLIMATE_ZONES_BA
        self.climate_zones_iecc = CLIMATE_ZONES_IECC

        # Geographic information
        self.df_geoinfo = self.get_geoinfo()

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
            df = pd.read_csv(url, index_col=["nhgis_county_gisjoin"])
        except Exception as err:
            raise Exception(f"{err} (URL='{url}')")

        # Get county names
        self.df_geoinfo_full = df

        df = df[df[f"{sector}_county_id"].str.contains("Not Applicable") == False]
        county_names = [x.split(" ")[1:-1] if x.endswith("County") else x.split(" ")[1:] for x in
                        df[f"{sector}_county_id"]]
        county_names = [" ".join(x) for x in county_names]
        df = df.assign(county_name=county_names)
        return df

    def get_metadata(self, sector):
        sector = sector.lower()

        filename = "metadata/metadata.parquet"

        url = self.paths_amy_2018_v1["end_use_loads"] + \
              self.paths_amy_2018_v1[sector] + \
              f"{filename}"

        try:
            df = pd.read_parquet(url)
        except Exception as err:
            raise Exception(f"{err} (URL='{url}')")

        # Only using these cols for now
        if sector.lower() == "resstock":
            df = df[["in.county", "in.geometry_building_type_recs", "in.sqft"]]
            df = df.rename(columns=
            {
                "in.county":"county",
                "in.geometry_building_type_recs": "building_type",
                "in.sqft":"sqft"
            }
            )
        if sector.lower() == "comstock":
            df = df[["in.county", "in.building_type", "in.sqft"]]
            df = df.rename(columns=
            {
                "in.county":"county",
                "in.building_type": "building_type",
                "in.sqft":"sqft"
            }
            )
        return df

    def get_weather(self, county_gisjoin):
        # This file is identical between ResStock and Comstock
        # TODO double check the above
        sector = "resstock"
        filename = f"{county_gisjoin.upper()}_2018.csv"

        url = self.paths_amy_2018_v1["end_use_loads"] + \
              self.paths_amy_2018_v1[sector] + \
              "weather/amy2018/" + \
              f"{filename}"

        try:
            df = pd.read_csv(url, index_col=["date_time"])
        except Exception as err:
            raise Exception(f"{err} (URL='{url}')")

        return df

    def get_county_gisjoin_name(self, county_name=None, state=None, county_gisjoin=None):
        if county_name and state:
            try:
                return \
                self.df_geoinfo[(self.df_geoinfo["county_name"] == county_name.capitalize()) & \
                                (self.df_geoinfo["state_abbreviation"] == state.upper())].index[0]
            except IndexError as e:
                print(e)
                raise IndexError("Likely error: county name does not exist in specified state.")
        elif county_gisjoin:
            return self.df_geoinfo.iloc[self.df_geoinfo.index == county_gisjoin.capitalize()][
                "county_name"].values[0]
        else:
            raise Exception("Must provide state and county name, or county GISJOIN.")

    # TODO: validate that options exist in class attribute sets
    # TODO: set up cache

    def get_data_by_state(self, sector, state, building_type, upgrade=0):
        """Pulls CSV"""
        state = state.upper()
        sector = sector.lower()

        if self.release_year > 2021:
            upgrade = f"upgrade={upgrade}/"
            filename = f"up{upgrade:02}-{state.lower()}-{building_type}.csv"
        else:
            upgrade = ""
            filename = f"{state.lower()}-{building_type}.csv"

        timeseries_aggregate_state = f"timeseries_aggregates/" \
                                     f"by_state/" \
                                     f"{upgrade}" \
                                     f"state={state}/" \
                                     f"{filename}"

        url = self.paths_amy_2018_v1["end_use_loads"] + \
              self.paths_amy_2018_v1[sector] + \
              timeseries_aggregate_state
        try:
            df = pd.read_csv(url, index_col=["timestamp"])
        except Exception as err:
            raise Exception(f"{err} (URL='{url}')")
        df.index = pd.to_datetime(df.index)
        return df

    def get_data_by_county(self, sector, state, building_type, county_gisjoin=None, county_name=None):
        """Pulls CSV"""
        state = state.upper()
        sector = sector.lower()

        if county_name and not county_gisjoin:
            county_gisjoin = self.get_county_gisjoin_name(county_name=county_name, state=state)

        filename = f"{county_gisjoin.lower()}-{building_type.lower()}.csv"
        timeseries_aggregate_county = f"timeseries_aggregates/" \
                                      f"by_county/" \
                                      f"state={state.upper()}/" \
                                      f"{filename}"

        url = self.paths_amy_2018_v1["end_use_loads"] + \
              self.paths_amy_2018_v1[sector] + \
              timeseries_aggregate_county
        try:
            df = pd.read_csv(url, index_col=["timestamp"])
        except Exception as err:
            raise Exception(f"{err} (URL='{url}')")
        df.index = pd.to_datetime(df.index)
        return df

    def get_data_by_climate_ba(self, sector, climate, building_type, upgrade=0):
        """Pulls CSV"""
        climate_zone = climate.lower()
        sector = sector.lower()

        # for some reason "Very Cold" climate zone naming is set up differently
        if climate == "very-cold":
            climate = "very_cold"
            climate_zone = "Very%20Cold"

        if self.release_year > 2021:
            upgrade = f"upgrade={upgrade}/"
            filename = f"up{upgrade:02}-{climate}-{building_type}.csv"
            timeseries_aggregate_climate = f"timeseries_aggregates/" \
                                           f"by_building_america_climate_zone/" \
                                           f"{upgrade}" \
                                           f"building_america_climate_zone={climate_zone}/" \
                                           f"{filename}"
        else:
            filename = f"{climate}-{building_type}.csv"
            timeseries_aggregate_climate = f"timeseries_aggregates/" \
                                           f"by_building_america_climate_zone/" \
                                           f"{filename}"

        url = self.paths_amy_2018_v1["end_use_loads"] + \
              self.paths_amy_2018_v1[sector] + \
              timeseries_aggregate_climate

        df = pd.read_csv(url, index_col=["timestamp"])
        df.index = pd.to_datetime(df.index)
        return df

    def get_data_by_climate_iecc(self, sector, climate, building_type, upgrade=0):
        """Pulls CSV"""
        climate = climate.upper()
        sector = sector.lower()

        if self.release_year > 2021: # Note that comstock does not have any iecc climate data for 2022
            upgrade = f"upgrade={upgrade}/"
            filename = f"up{upgrade:02}-{climate}-{building_type}.csv"
        else:
            upgrade = ""
            filename = f"{climate}-{building_type}.csv"

        timeseries_aggregate_climate = f"timeseries_aggregates/" \
                                       f"by_ashrae_iecc_climate_zone_2004/" \
                                       f"{upgrade}" \
                                       f"ashrae_iecc_climate_zone_2004={climate.upper()}/" \
                                       f"{filename}"

        url = self.paths_amy_2018_v1["end_use_loads"] + \
              self.paths_amy_2018_v1[sector] + \
              timeseries_aggregate_climate

        df = pd.read_csv(url, index_col=["timestamp"])
        df.index = pd.to_datetime(df.index)
        return df
