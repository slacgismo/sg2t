"""Class for loadshape analysis.
Data passed to this class should be in sg2t format ideally
imported through sg2t.io.
"""

import pandas as pd
from sg2t.utils import Timeseries
from sg2t.utils.io import load_metadata

class Loadshape(Timeseries):
    """Loadshape manipulation and analysis.
    Instantiate with data from sg2t.io or sg2t
    formatted pd.DataFrame. Timeseries (time axis)
    manipulation inherited from the Timeseries class.
    """
    def __init__(self, data, metadata=None, metadata_file=None):
        self.data = data
        self.metadata = metadata
        self.metadata_file = metadata_file
        if not metadata and metadata_file is not None:
            # TODO: validate that it's in json format
            self.metadata = self.load_metadata(self.metadata_file)

    def validate_data(self):
        """Validate that imported data is in correct format.
        First column: Data as datetime.date object
        Second column: Time as datetime.time object
        Third+ column: Load values (float)
        """
        # TODO: implement
        pass
