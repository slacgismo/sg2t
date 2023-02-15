"""Test module for the io.loadshapes.nrel.ResStock class"""
import unittest
import os
from sg2t.io.loadshapes.nrel import ResStock

# TODO: remove dependencies on other methods
package_dir = os.environ["SG2T_HOME"]
# TMY3 test data
test_dir =  os.path.abspath(__file__ + "/../") + "/data"

class TestResStock(unittest.TestCase):

    def test_load_weather_location(self):
        files_dir = f"{package_dir}/io/loadshapes/nrel/"

        rs  = ResStock(
            metadata_file=files_dir+"resstock.json"
        )
        self.assertEqual(
            rs.load_weather_location(), "None")

    def test_get_data(self):
        files_dir = f"{package_dir}/io/loadshapes/nrel/"
        test_data = f"{test_dir}/resstock_tmy3_loads/AL_bldg_100066-0.parquet"

        len_data = 35040
        bldg_id = 100066
        len_cols = 12 # defined in _format_data() method

        rs  = ResStock(
            metadata_file=files_dir+"resstock.json"
        )
        data = rs.get_data(test_data)

        self.assertEqual(len_data, len(data))
        self.assertEqual(bldg_id, data.index[0])
        self.assertEqual(len_cols, len(data.columns))

    def test_format_data(self):
        pass

    def test_export_data(self):
        files_dir = f"{package_dir}/io/loadshapes/nrel/"
        test_data = f"{test_dir}/resstock_tmy3_loads/AL_bldg_100066-0.parquet"

        len_data = 35040
        bldg_id = 100066
        len_cols = 12  # defined in _format_data() method

        rs = ResStock(
            metadata_file=files_dir + "resstock.json"
        )
        data = rs.get_data(test_data)
        files = rs.export_data(type="CSV")

        self.assertEqual(len_data, len(data))
        self.assertEqual(bldg_id, data.index[0])
        self.assertEqual(isinstance(files[0], str), True)

if __name__ == '__main__':
    unittest.main()