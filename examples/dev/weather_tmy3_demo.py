from sg2t.io.weather import tmy3
import os

package_dir = os.path.abspath(__file__ + "/../../")
files_dir = f"{package_dir}/sg2t/io/weather/data/tmy3/"
config_dir = f"{package_dir}/sg2t/config/"

# import some data using TMY3 module
# defaults work
tmy = tmy3.TMY3(
    # config_name=config_dir + "config.ini",
    # config_key="data.tmy3",
    # metadata_file= f"{package_dir}/sg2t/io/weather/tmy3/" + "tmy3_nrel.json"
)

# pick a weather station
st_10 = tmy.get_index()[1]
print(f"Station {st_10[:-4]}")

data = tmy.get_raw_data(st_10)

#print("First 100 elements: ", data[:100])

# need to split up into rows/import as dataframe
tmy.get_dataframe(data)
#
tmy.data.head()