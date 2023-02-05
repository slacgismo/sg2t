import unittest
import os
from sg2t.io.weather.tmy3 import TMY3

# TODO: remove dependencies on other methods
package_dir = os.environ["SG2T_HOME"]
# TMY3 test data
test_dir =  os.path.abspath(__file__ + "/../") + "/data/tmy3/US/"

class TestTMY3(unittest.TestCase):

    def test_get_index(self):
        files_dir = f"{package_dir}/io/weather/tmy3/"

        tmy3  = TMY3(
            config_name="config.ini",
            config_key="data.tmy3",
            metadata_file=files_dir+"tmy3_nrel.json"
        )
        self.assertEqual(tmy3.get_index(test_dir)[0], "AK-Adak_Nas.tmy3")

    def test_get_data(self):
        files_dir = f"{package_dir}/io/weather/tmy3/"
        config_dir = f"{package_dir}/config/"

        station_file = test_dir + "AK-Adak_Nas.tmy3"
        first_temp = 0.2
        len_data = 8760 # nrows

        tmy3 = TMY3(
            config_name="config.ini",
            config_key="data.tmy3",
            metadata_file=files_dir+"tmy3_nrel.json"
        )
        data = tmy3.get_data(station_file)
        self.assertEqual(len_data, len(data))
        self.assertEqual(first_temp, data["Temperature"][0])

    def test_format_data(self):
        pass

    def test_export_data(self):
        pass

if __name__ == '__main__':
    unittest.main()