import unittest
from sg2t.io.tmy3 import TMY3

class TestTMY3(unittest.TestCase):

    def test_1_get_index(self):
        self.assertEqual(get_index()[0],"AK-Adak_Nas.tmy3")

    def test_2_get_data(self):
        station = get_index()[0]
        tmy3 = get_tmy3(station,coerce_year=2020)
        self.assertEqual(tmy3.drybulb[0],0.2)
        self.assertEqual(tmy3.units['drybulb'],"degC")

if __name__ == '__main__':
    unittest.main()