"""
====================================
Import TMY3 data and obtain dataframe
====================================
This example demonstrates how to import a TMY data
file and read it with the sg2t.weather package.
"""
# TODO Use `sg2t.utils.data` to download the file

import os
from pathlib import Path

from sg2t.io.tmy3 import TMY3, get_index
from sg2t.weather import Weather

##############################################################################
# Import the data file to read. Here we use locally stored NREL TMY3 data.

package_dir = Path.cwd().parent.parent
country = "US"
cache_dir = f"{package_dir}/weather/data/tmy3/{country}/"

# Select a weather station from the index
station = get_index[3]
data_file = cache_dir + station
tmy_data = TMY3(data_file)

# Metadata should include: state, station name, year, longitude, latitude, ?
tmy_data.metadata()

# Export data in format suitable for sg2t analysis
# Other options should include CSV file
sg2t_weather_data = tmy_data.export("sg2t")

##############################################################################
# Instantiate a Weather class while passing the data

weather_station_X = Weather(data=sg2t_weather_data)
# return pandas df

# at instantiation class should check format of passed data based on sg2t data schema
# return an error if not formatted correctly?


# query the dataframe and aggregate it as needed etc
weather_station_X.plot("hourly") # etc?

# can get HI for example
HI = weather_station_X.get_heat_index()

##############################################################################
# Specific applications:
# format should be directly passable to sg2t.alm or sg2t.lca
# and those modules should be able to select needed columns
# for example for development of hourly weather sensitivity factors
import sg2t.lca import CompositionAnalysis

# Below would follow NERC's LCA methodology
some_data = "some_load_data"
ca = CompositionAnalysis(load_data=some_data, weather_data=weather_station_X)
ca.decompose(weather_sensitive=True)



