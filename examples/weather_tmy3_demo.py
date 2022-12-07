from sg2t.io.weather import tmy3
import os

package_dir = os.path.abspath(__file__ + "/../../")
files_dir = f"{package_dir}/sg2t/io/weather/data/tmy3/"
config_dir = f"{package_dir}/sg2t/config/"

# import some data using TMY3 module
tmy = tmy3.TMY3(
    config_name=config_dir + "config.ini",
    config_key="data.tmy3",
    metadata_file= f"{package_dir}/sg2t/io/weather/tmy3/" + "tmy3_nrel.json"
)

tmy.get_data("AK-Adak_Nas.tmy3")

#tmy.get_data(idx[0])