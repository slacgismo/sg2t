"""Test module for the io.loadshape.Loadshape class"""

import unittest
import os
from sg2t.loadshape import Loadshape

package_dir = os.environ["SG2T_HOME"]
# Loadshape test data
test_dir =  os.path.abspath(__file__ + "/../") + "/data"

test_resstock = "resstock_2023-02-04_18-27-36-39.csv"
test_resstock_meta = "metadata_resstock_2023-02-04_18-27-36-39.json"

class TestLoadshape(unittest.TestCase):
