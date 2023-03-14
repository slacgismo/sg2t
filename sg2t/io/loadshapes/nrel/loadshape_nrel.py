import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sg2t.io.loadshapes.nrel.api import API

# this is temporary until we generalize the mapping
SG2T_COL= {
    "timestamp": "Datetime",
    "out.electricity.cooling.energy_consumption.kwh": "Electricity Cooling",
    "out.electricity.heating.energy_consumption.kwh": "Electricity Heating",
    "out.fuel_oil.heating.energy_consumption.kwh": "Fuel Oil Heating",
    "out.natural_gas.heating.energy_consumption.kwh": "Natural Gas Heating",
    "out.propane.heating.energy_consumption.kwh": "Propane Heating",
    "out.site_energy.total.energy_consumption.kwh": "Site Energy Total",
    "out.electricity.total.energy_consumption.kwh": "Electricity Total",
    "out.fuel_oil.total.energy_consumption.kwh": "Fuel Oil Total",
    "out.natural_gas.total.energy_consumption.kwh": "Natural Gas Total",
    "out.propane.total.energy_consumption.kwh": "Propane Total",
    "out.electricity.cooling.energy_consumption": "Electricity Cooling",
    "out.electricity.heating.energy_consumption": "Electricity Heating",
    "out.fuel_oil.heating.energy_consumption": "Fuel Oil Heating",
    "out.natural_gas.heating.energy_consumption": "Natural Gas Heating",
    "out.propane.heating.energy_consumption": "Propane Heating",
    "out.site_energy.total.energy_consumption": "Site Energy Total",
    "out.electricity.total.energy_consumption": "Electricity Total",
    "out.fuel_oil.total.energy_consumption": "Fuel Oil Total",
    "out.natural_gas.total.energy_consumption": "Natural Gas Total",
    "out.propane.total.energy_consumption": "Propane Total"
}

class LoadShapeAggregation:
    """
    Loadshape analysis for Resstock and Commstock energy consumption data from api.py

    Example
    -------
    >>> loadshape_module = LoadShapeAggregation()
    >>> df = loadshape_module.loadshape_by_state_resstock(state = "CA", home_type = "mobile_type)
    >>> print(df)
                Electricity Cooling  Electricity Heating  Fuel Oil Heating  ...  Fuel Oil Total  Natural Gas Total  Propane Total
        0          31338.122088        114279.874287     154976.407965  ...   166299.458831      577459.138057  203219.075954
        1          30245.812039        114570.220550     152104.897449  ...   162479.477774      567214.527878  199913.434647
        2          28697.412074        117792.909368     155967.704119  ...   165603.825037      573633.118655  203525.301482
        3          27387.184114        120132.038903     157454.701815  ...   166539.489439      574924.474650  204571.950208
        4          26031.538347        122470.430768     159832.074473  ...   168544.904163      578238.254571  206792.521654
        ..                  ...                  ...               ...  ...             ...                ...            ...
        91         40839.494939        104605.957549     147517.411528  ...   164017.116775      573674.660545  198374.937303
        92         38623.531812        106848.928567     149851.002632  ...   165192.743934      577235.161295  200401.030236
        93         36812.789860        106380.877378     147007.290008  ...   161396.885932      566980.240493  196762.765687
        94         34801.113000        109444.192247     150919.473117  ...   164150.040090      574085.389561  200440.441722
        95         33081.157574        111832.520150     152532.573261  ...   164710.691904      575070.520222  201443.766158

        [96 rows x 10 columns]
    """

    def __init__(self, aggregation = 'avg', month_start = 1, month_end = 12):
        """ 
        Parameters
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

        """         
        self.nrel_api = API()
        self.aggregation = aggregation
        self.month_start = month_start
        self.month_end = month_end

    def loadshape_aggregation(self, df: pd.DataFrame) -> pd.DataFrame: 
        """takes timeseries energy consumption data for a year then perform aggregation and returns a loadshape dataframe for 24hrs"""

        # rename columns using sg2t_col and drop the rest of the columns
        df.rename(columns=SG2T_COL, inplace = True)
        df = df[df.columns.intersection([*SG2T_COL.values()])]

        # filter data by month (could be for a specific month or for a range of months)
        df_month = df[df.index.month.isin([i for i in range(self.month_start, self.month_end)])]

        # aggregate data using groupby with the corrosponding aggregation type
        if self.aggregation == 'avg':
            df_aggregated = df_month.groupby([(df_month.index.hour),(df_month.index.minute)]).mean()
        elif self.aggregation == 'sum':
            df_aggregated = df_month.groupby([(df_month.index.hour),(df_month.index.minute)]).sum()
        elif self.aggregation == 'peak_day':
            # find peak load day based on "Electricity Total" column
            peak_day = df[df["Electricity Total"] == df["Electricity Total"].max()].index[0]
            df_aggregated = df[(df.index.day == peak_day.day) & (df.index.month == peak_day.month)]
        else:
            print('Error: Aggregation input is not right')
            df_aggregated = pd.DataFrame()

        df_aggregated = df_aggregated.reset_index(drop=True)
        return df_aggregated

    def get_residential_loadshape_by_state(self, state: str, home_type: str) -> pd.DataFrame:
        """ pulls resstock energy data by state and home_type and uses the aggregate function to return a loadshape dataframe"""
        df = self.nrel_api.get_data_resstock_by_state(state, home_type)
        df_aggregated = self.loadshape_aggregation(df)
        return df_aggregated

    def get_residential_loadshape_by_climatezone(self, climate: str, home_type: str) -> pd.DataFrame:
        """ pulls resstock energy data by climate zone and home_type and uses the aggregate function to return a loadshape dataframe"""
        df = self.nrel_api.get_data_resstock_by_climatezone(climate, home_type)
        df_aggregated = self.loadshape_aggregation(df)
        return df_aggregated

    def get_commercial_loadshape_by_state(self, state: str, building_type: str) -> pd.DataFrame:
        """ pulls commstock energy data by state and building_type and uses the aggregate function to return a loadshape dataframe"""
        df = self.nrel_api.get_data_comstock_by_state(state, building_type)
        df_aggregated = self.loadshape_aggregation(df)
        return df_aggregated

    def get_commercial_loadshape_by_climatezone(self, climate: str, building_type: str) -> pd.DataFrame:
        """ pulls commstock energy data by climate zone and building_type and uses the aggregate function to return a loadshape dataframe"""
        df = self.nrel_api.get_data_comstock_by_climatezone(climate, building_type)
        df_aggregated = self.loadshape_aggregation(df)
        return df_aggregated

    def plot_loadshape(self, df):
        """plot the loadshape"""
        t = np.linspace(0,24,len(df))
        plt.plot(t, df["Electricity Total"])
        plt.xlabel('Hour of the day')
        plt.ylabel('Electric Consumption (kWh)')
        plt.grid()
        plt.show()