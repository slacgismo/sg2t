import pandas as pd
from sg2t.loadshape import Data

class ResStock(Data):
    """Module for importing data from NREL's ResStock
     dataset into sg2t tools.
    """
    def read_data(self):
        """Read in data from arbitrary source
        and return data in defined structure:
        Col1: datetime
        Col2: power (kW)
        Col3+: other
        """
        self.data = self.data.set_index(["timestamp"])
        total_kW = "out.site_energy.total.energy_consumption.kW"
        total_kWh = "out.site_energy.total.energy_consumption"
        self.data[total_kW] = self.data[total_kWh]*0.25
        column = self.data.pop(total_kW)
        self.data.insert(0, total_kW, column)
        return self.data