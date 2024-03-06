"""Class for timeseries data with methods of common time axis manipulations."""
import datetime
import pandas as pd

class Timeseries:
    def __init__(self, data):
        self.data = data
        self.daytypes = ["weekday", "weekend"]

    def merge_date_time(self, data_df, date_key: str, time_key: str):
        """Combine date and time cols into one Datetime column"""
        data_df["Datetime"] = data_df[date_key].astype(str) + " " + data_df[time_key].astype(str)
        data_df.drop([date_key, time_key], inplace=True, axis=1)
        return data_df

    @staticmethod
    def make_datetime(series):
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

    @staticmethod
    def timeseries_aggregate(df, aggregation = 'avg', month_start = 1, month_end = 12, daytype = None):
        """ 
        Takes timeseries data then perform aggregation and returns a aggregated dataframe for 24hrs. 

        Parameters
        ----------
        df: pd.DataFrame
            dataframe where index is datatime type and include other column/s with numbers

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

         daytype: str
            filters data based on daytype: if it's weekday (Mon-Fri) or weekend (Sat-Sun)
            default is set to None which doesn't do any daytype filtering

        """   
        # check to make sure dataframe passed is in the correct form
        if not isinstance(df.index, pd.DatetimeIndex):
            raise NotImplementedError("Dataframe index is not pd.DatetimeIndex type; convert index to datetime formate before passing dataframe") 

        # remove last row as df includes next year first data point (01-01 00:00:00)      
        df = df[:-1] 

        # filter data by month (could be for a specific month or for a range of months)
        df = df[df.index.month.isin([i for i in range(month_start, month_end)])]

        # filter data by daytype
        if daytype == 'weekday':
            df = df[df.index.weekday <= 4]
        elif daytype == 'weekend':
            df = df[df.index.weekday > 4]
        elif daytype == None:
            df = df
        else: 
            raise ValueError('Error: Weekday input is not right; have to use either "weekday" or "weekend" ')

        # aggregate data using groupby with the corresponding aggregation type
        if aggregation == 'avg':
            df_aggregated = df.groupby([(df.index.hour),(df.index.minute)]).mean(numeric_only=True)
        elif aggregation == 'sum':
            df_aggregated = df.groupby([(df.index.hour),(df.index.minute)]).sum(numeric_only=True)
        elif aggregation == 'peak_day':
            # find peak load day based on "Electricity Total" column
            peak_day = df[df["Electricity Total"] == df["Electricity Total"].max()].index[0]
            df_aggregated = df[(df.index.day == peak_day.day) & (df.index.month == peak_day.month)]
        else:
            raise ValueError('Error: Aggregation input is not right; have to use one of the following: "avg", "sum", "peak_day" ')

        # change index and group by each hour
        df_aggregated.index.names = ['hour', 'minute']
        df_aggregated.reset_index(inplace=True)
        df_aggregated['datetime'] = pd.to_datetime(df_aggregated['hour'].astype(str) + ':' + df_aggregated['minute'].astype(str), format='%H:%M')

        # Set datetime as the index
        df_aggregated.set_index('datetime', inplace=True)
        df_resampled = df_aggregated.resample('h').mean()
        df_resampled = df_resampled.drop(['hour', 'minute'], axis=1)
        return df_resampled.reset_index(drop=True)

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
        