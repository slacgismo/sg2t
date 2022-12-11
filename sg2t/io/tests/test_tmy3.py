import unittest
import os
from sg2t.io.weather.tmy3 import TMY3

# TODO: remove dependencies on other methods

class TestTMY3(unittest.TestCase):

    def test_get_index(self):
        package_dir = os.path.abspath(__file__ + "/../../../")
        files_dir = f"{package_dir}/io/weather/tmy3/"
        config_dir = f"{package_dir}/config/"

        print(files_dir)
        tmy3  = TMY3(
            config_name=config_dir+"config.ini",
            config_key="data.tmy3",
            metadata_file=files_dir+"tmy3_nrel.json"
        )
        self.assertEqual(tmy3.get_index()[0], "AK-Adak_Nas.tmy3")

    def test_get_data(self):
        package_dir = os.path.abspath(__file__ + "/../../../")
        files_dir = f"{package_dir}/io/weather/tmy3/"
        config_dir = f"{package_dir}/config/"

        station_file = "AK-Adak_Nas.tmy3"
        last_chars = "9,00,C,8\n"
        len_data = 1724999

        tmy3 = TMY3(
            config_name=config_dir + "config.ini",
            config_key="data.tmy3",
            metadata_file=files_dir + "tmy3_nrel.json"
        )
        data = tmy3.get_data(station_file)
        self.assertEqual(len_data, len(data))
        self.assertEqual(last_chars, data[-9:])

    # def test_get_data(self):
    #     tmy3 = TMY3()
    #     station = tmy3.get_index()[0]
    #     tmy3 = get_tmy3(station,coerce_year=2020)
    #     self.assertEqual(tmy3.drybulb[0],0.2)
    #     self.assertEqual(tmy3.units['drybulb'],"degC")

if __name__ == '__main__':
    unittest.main()