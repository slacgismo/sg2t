"""Class for timeseries data with methods of common time axis manipulations."""
import datetime
import pandas as pd

class Timeseries():
    def __init__(self, data):
        self.data = data
        self.daytypes = ["weekday", "weekend"]

    def merge_date_time(self, data_df, date_key: str, time_key: str):
        """Combine date and time cols into one Datetime column"""
        data_df["Datetime"] = data_df[date_key].astype(str) + " " + data_df[time_key].astype(str)
        data_df.drop([date_key, time_key], inplace=True, axis=1)
        return data_df

    def make_datetime(self, series):
        """Make series vals Datetime objects"""
        try:
            series = pd.to_datetime(series)
        except ValueError as e:
            e = str(e)
            if e[:21] == "hour must be in 0..23":
                # Data set needs cleaning to convert to
                # hours following 00-23 format
                series = self.convert_hour_type(series)
                series = pd.to_datetime(series)
            else:
                raise NotImplementedError("Datetime exception not handled.")
        return series

    def convert_hour_type(self, series):
        """Method to convert hours to 00-23 format"""
        for i in range(len(series)):
            date = series[i]
            date_str, time_str = date.split(" ")
            HH, MM = time_str.split(":")

            if HH == "24":
                HH = "00"
                date = date_str + " " + HH + ":" + MM
                series[i] = date
        return series

    # adjust below
    def get_daytype(self, value):
        """Default grouping function:
        Get the day type for a datetime value
        """
        for daytype, weekdays in daytypes.items():
            if value.weekday() in weekdays:
                return daytype
        return None

    def get_hour(self, x, dstrules):
        """Default grouping function:
        Get the hour of day for a datetime value
        """
        if x.year in dstrules:
            rule = dstrules[x.year]
            if x > rule[0] and x <= rule[1]:
                return x.hour + 1
        return x.hour

    def group_data(self):
        self.datecol = self.data.columns[0]
        self.daytypes = {
            "weekday" : [0,1,2,3,4],
            "weekend" : [5,6],
            "holiday" : [7],
            }
        self.dstrules = {}
        self.groupby = {
            "daytype":[self.datecol,get_daytype,self.daytypes],
            "hour":[self.datecol,get_hour,self.dstrules]
            }
        self.columns = self.data.columns[1:]
        self.add_groups()
        if not_valid:
            return Exception

        valid = True
        return valid

def timeseries_aggregate(df, aggregation = 'avg', month_start = 1, month_end = 12):
        """ 
        Takes timeseries data for a year then perform aggregation and returns a aggregated dataframe for 24hrs. 

        Parameters
        ----------
        df: pd.DataFrame
            dataframe where index is datatime type that includes data for a whole year

        aggregation: str 
            default is set as 'avg' which takes the average values for each timestep in the day
            other options: 
                'sum': take the sum across the timeperiod for each timestep in the day
                'peak_day': filters the peak_day loadshape

        month_start, month_end : int
            month range for aggregation, default is set to aggregate for the whole year (month_start = 1, month_end = 12)
            for example: 
                Aggregation for a specific month e.g. January; month_start = 1, month_end = 2
                Aggregation for a season e.g. Summer (June, July, August); month_start = 6, month_end = 9 
        """   
        # check to make sure dataframe passed is in the correct form
        if not isinstance(df.index, pd.DatetimeIndex):
            raise NotImplementedError("Dataframe index is not pd.DatetimeIndex type; convert index to datetime formate before passing dataframe") 

        # filter data by month (could be for a specific month or for a range of months)
        df_month = df[df.index.month.isin([i for i in range(month_start, month_end)])]

        # aggregate data using groupby with the corrosponding aggregation type
        if aggregation == 'avg':
            df_aggregated = df_month.groupby([(df_month.index.hour),(df_month.index.minute)]).mean()
        elif aggregation == 'sum':
            df_aggregated = df_month.groupby([(df_month.index.hour),(df_month.index.minute)]).sum()
        elif aggregation == 'peak_day':
            # find peak load day based on "Electricity Total" column
            peak_day = df[df["Electricity Total"] == df["Electricity Total"].max()].index[0]
            df_aggregated = df[(df.index.day == peak_day.day) & (df.index.month == peak_day.month)]
        else:
            raise ValueError('Error: Aggregation input is not right; have to use one of the following: "avg", "sum", "peakday" ')  

        df_aggregated = df_aggregated.reset_index(drop=True)
        return df_aggregated