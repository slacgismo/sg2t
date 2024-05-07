from turtle import home
from typing import Optional
import pandas as pd
from sg2t.io.loadshapes.nrel.api import API
from sg2t.utils.timeseries import Timeseries
from sg2t.io.loadshapes.nrel.naming import CLIMATE_ZONES, HOME_TYPES, BUILDING_TYPES, NREL_COL_MAPPING

class LoadshapeNrel:
    """ Loadshape analysis for Resstock and Comstock energy consumption data from pulled from NREL directly using api.py"""

    def __init__(self, aggregation = 'avg', month_start = 1, month_end = 12, daytype = None):
        """ 
        PARAMETERS
        ----------
        aggregation: str 
            default is set as 'avg' which takes the average values for each timestep in the day
            other options: 
                'sum': take the sum across the timeperiod for each timestep in the day
                'peak_day': filters the peak_day loadshape

        month_start, month_end : int
            month range for aggregation, default is set to aggregate for the whole year (month_start = 1, month_end = 12)
            for example: 
                if aggregation is wanted for a specific month e.g. January; month_start = 1, month_end = 2
                if aggregation is wanted for a season e.g. Summer (June, July, August); month_start = 6, month_end = 9 
        
         daytype: str
            filters data based on daytype: if it's weekday (Mon-Fri) or weekend (Sat-Sun)
            default is set to None which doesn't do any daytype filtering

        """         
        self.nrel_api = API() # TODO: use dependency injection instead
        self.aggregation = aggregation
        self.month_start = month_start
        self.month_end = month_end
        self.daytype = daytype

    def _format_columns_df(self, df):
         # rename columns using NREL_COL_MAPPING and drop the rest of the columns
        df.rename(columns=NREL_COL_MAPPING, inplace = True)
        df = df[df.columns.intersection([*NREL_COL_MAPPING.values()])]
        return df

    def get_resstock_loadshape_by_state(self, state: str, home_type: Optional[str] = None) -> pd.DataFrame:
        """ pulls resstock energy data by state and home_type and uses the timeseries aggregate function to return a 24hr loadshape dataframe
        
        PARAMETERS
        ----------
        state: str
            US State to pull data from NREL timeseries aggregate/by_state

        home_type: str
            home type (mobile_home, single-family_detached, single-family_attached, etc...)
            if none provided, it sums up all the home types energy consumption to get a total loadshape for all the state's residential sector energy consumption

        RETURNS
        -------
        df: pd.DataFrame
            returns a dataframe with 24hr loadshape for the state's residential/resstock energy consumption
        """
        if home_type == None:
            # sums up all types of homes (single-family detatched, apartments, etc..)
            df = 0 # initialization to be able to add all the dataframes together
            for home_type in HOME_TYPES:
                df_ = self.nrel_api.get_data_resstock_by_state(state, home_type)
                df_ = self._format_columns_df(df_)
                df += Timeseries.timeseries_aggregate(df_, self.aggregation, self.month_start, self.month_end, self.daytype)
        else:
            df_ = self.nrel_api.get_data_resstock_by_state(state, home_type)
            df_ = self._format_columns_df(df_)
            df = Timeseries.timeseries_aggregate(df_, self.aggregation, self.month_start, self.month_end, self.daytype)
        return df

    def get_resstock_loadshape_by_climatezone(self, climate: str, home_type: Optional[str] = None) -> pd.DataFrame:
        """ pulls resstock energy data by climate zone and home_type and uses the aggregate function to return a 24hr loadshape dataframe

        PARAMETERS
        ----------
        climate: str
            climate zone (cold, hot-humid, marine, etc...)

        home_type: str
            home type (fullservicerestaurant, hospital, largeoffice, smalloffice, etc...)
            if none provided, it sums up all the home types energy consumption to get a total loadshape for all the climate zone's residential sector energy consumption

        RETURNS
        -------
        df: pd.DataFrame
            returns a dataframe with 24hr loadshape for the climate zone residential/resstock energy consumption
        """
        if home_type == None:
            # sums up all types of homes (single-family detatched, apartments, etc..)
            df = 0 # initialization to be able to add all the dataframes together
            for home_type in HOME_TYPES:
                df_ = self.nrel_api.get_data_resstock_by_climatezone(climate, home_type)
                df_ = self._format_columns_df(df_)
                df += Timeseries.timeseries_aggregate(df_, self.aggregation, self.month_start, self.month_end, self.daytype)
        else:
            df_ = self.nrel_api.get_data_resstock_by_climatezone(climate, home_type)
            df_ = self._format_columns_df(df_)
            df = Timeseries.timeseries_aggregate(df_, self.aggregation, self.month_start, self.month_end, self.daytype)
        return df

    def get_resstock_loadshape_by_climatezone_iecc(self, climate: str, home_type: Optional[str] = None) -> pd.DataFrame:
        """ pulls resstock energy data by iecc climate zone and home_type and uses the aggregate function to return a 24hr loadshape dataframe

        PARAMETERS
        ----------
        climate: str
            iecc climate zone (1A, 2A, 2B, ...)
            https://basc.pnnl.gov/images/iecc-climate-zone-map

        home_type: str
            home type (fullservicerestaurant, hospital, largeoffice, smalloffice, etc...)
            if none provided, it sums up all the home types energy consumption to get a total loadshape for all the climate zone's residential sector energy consumption

        RETURNS
        -------
        df: pd.DataFrame
            returns a dataframe with 24hr loadshape for the climate zone residential/resstock energy consumption
        """
        if home_type == None:
            # sums up all types of homes (single-family detatched, apartments, etc..)
            df = 0 # initialization to be able to add all the dataframes together
            for home_type in HOME_TYPES:
                df_ = self.nrel_api.get_data_resstock_by_climatezone_iecc(climate, home_type)
                df_ = self._format_columns_df(df_)
                df += Timeseries.timeseries_aggregate(df_, self.aggregation, self.month_start, self.month_end, self.daytype)
        else:
            df_ = self.nrel_api.get_data_resstock_by_climatezone_iecc(climate, home_type)
            df_ = self._format_columns_df(df_)
            df = Timeseries.timeseries_aggregate(df_, self.aggregation, self.month_start, self.month_end, self.daytype)
        return df

    def get_resstock_loadshape_total(self) -> pd.DataFrame:
        """gets the total residential/resstock loadshape for the whole US by summing up all the climate zones loadshapes for all home types"""
        total_resstock_df = 0 # initialization to be able to add all the dataframes together
        for climate in CLIMATE_ZONES:
            total_resstock_df += self.get_resstock_loadshape_by_climatezone(climate)
        return total_resstock_df

    def get_comstock_loadshape_by_state(self, state: str, building_type: Optional[str] = None) -> pd.DataFrame:
        """ pulls comstock energy data by state and building_type and uses the timeseries aggregate function to return a 24hr loadshape dataframe
        
        PARAMETERS
        ----------
        state: str
            US State to pull data from NREL timeseries aggregate/by_state

        building_type: str
            building type (fullservicerestaurant, hospital, largeoffice, smalloffice, etc...)
            If none provided, it sums up all the building types energy consumption to get a total loadshape for all the state's commercial sector energy consumption

        RETURNS
        -------
        df: pd.DataFrame
            returns a dataframe with 24hr loadshape for the state's commercial/comstock energy consumption
        """

        if building_type == None:
            # sums up all building types (fullservicerestaurant, hospital, largeoffice, etc..)
            df = 0 # initialization to be able to add all the dataframes together
            for building_type in BUILDING_TYPES:
                df_ = self.nrel_api.get_data_comstock_by_state(state, building_type)
                df_ = self._format_columns_df(df_)
                df += Timeseries.timeseries_aggregate(df_, self.aggregation, self.month_start, self.month_end, self.daytype)
        else:
            df_ = self.nrel_api.get_data_comstock_by_state(state, building_type)
            df_ = self._format_columns_df(df_)
            df = Timeseries.timeseries_aggregate(df_, self.aggregation, self.month_start, self.month_end, self.daytype)
        return df

    def get_comstock_loadshape_by_climatezone(self, climate: str, building_type: Optional[str] = None) -> pd.DataFrame:
        """ pulls comstock energy data by climate zone and building_type and uses the aggregate function to return a 24hr loadshape dataframe
        if building_type is not provided, it sums all the building types to get a total loadshape for all the commercial sector for that climate zone

        PARAMETERS
        ----------
        climate: str
            climate zone (cold, hot-humid, marine, etc...)

        building_type: str
            home type (fullservicerestaurant, hospital, largeoffice, smalloffice, etc...)
            if none provided, it sums up all the building types energy consumption to get a total loadshape for all the climate zone commercial sector energy consumption

        RETURNS
        -------
        df: pd.DataFrame
            returns a dataframe with 24hr loadshape for the climate zone commercial/comstock energy consumption
        """
        if building_type == None:
            # sums up all building types (fullservicerestaurant, clinics, schools, etc..)
            df = 0 # initialization to be able to add all the dataframes together
            for building_type in BUILDING_TYPES:
                df_ = self.nrel_api.get_data_comstock_by_climatezone(climate, building_type)
                df_ = self._format_columns_df(df_)
                df += Timeseries.timeseries_aggregate(df_, self.aggregation, self.month_start, self.month_end, self.daytype)
        else:
            df_ = self.nrel_api.get_data_comstock_by_climatezone(climate, building_type)
            df_ = self._format_columns_df(df_)
            df = Timeseries.timeseries_aggregate(df_, self.aggregation, self.month_start, self.month_end, self.daytype)  
        return df

    def get_comstock_loadshape_by_climatezone_iecc(self, climate: str, building_type: Optional[str] = None) -> pd.DataFrame:
        """ pulls comstock energy data by iecc climate zone and building_type and uses the aggregate function to return a 24hr loadshape dataframe
        if building_type is not provided, it sums all the building types to get a total loadshape for all the commercial sector for that climate zone

        PARAMETERS
        ----------
        climate: str
            iecc climate zone (1A, 2A, 2B, ...)
            https://basc.pnnl.gov/images/iecc-climate-zone-map

        building_type: str
            home type (fullservicerestaurant, hospital, largeoffice, smalloffice, etc...)
            if none provided, it sums up all the building types energy consumption to get a total loadshape for all the climate zone commercial sector energy consumption

        RETURNS
        -------
        df: pd.DataFrame
            returns a dataframe with 24hr loadshape for the climate zone commercial/comstock energy consumption
        """
        if building_type == None:
            # sums up all building types (fullservicerestaurant, clinics, schools, etc..)
            df = 0 # initialization to be able to add all the dataframes together
            for building_type in BUILDING_TYPES:
                df_ = self.nrel_api.get_data_comstock_by_climatezone_iecc(climate, building_type)
                df_ = self._format_columns_df(df_)
                df += Timeseries.timeseries_aggregate(df_, self.aggregation, self.month_start, self.month_end, self.daytype)
        else:
            df_ = self.nrel_api.get_data_comstock_by_climatezone_iecc(climate, building_type)
            df_ = self._format_columns_df(df_)
            df = Timeseries.timeseries_aggregate(df_, self.aggregation, self.month_start, self.month_end, self.daytype)  
        return df

    def get_comstock_loadshape_total(self) -> pd.DataFrame:
        """gets the total commercial/comstock loadshape for the whole US by summing up all the climate zones loadshapes for all building types"""
        total_comstock_df = 0 # initialization to be able to add all the dataframes together
        for climate in CLIMATE_ZONES:
            total_comstock_df += self.get_comstock_loadshape_by_climatezone(climate)
        return total_comstock_df
