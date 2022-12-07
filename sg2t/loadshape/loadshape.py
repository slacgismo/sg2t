import pandas as pd
import pyarrow.parquet as pq
from sg2t.loadshape import Base
from sg2t.loadshape.utils import get_daytype, get_hour

class Loadshape(Base):
    """Loadshape implementation requirements:
    - imports csv/df/parquet
    - loadshape and timestamps are min columns
    - returns df with ts and ls cols
    """
    def __init__(self, data_file: str=None, **kwargs):
        if data_file:
            self.data = None
            self.read_data(data_file, **kwargs)


    def read_data(self, file: str, **kwargs):
        """Read data file from different sources.
        Currently supporting:
        CSV, Excel sheets, AWS parquets, pandas DF
        """
        if file.lower().endswith('.csv'):
            self.data = pd.read_csv(file)
        elif file.lower().endswith('.xlsx'):
            self.data = pd.read_excel(file)
        elif file.lower().endswith('.parquet'):
            self.data = pq.read_pandas(file).to_pandas()
        else:
            self.data = pd.DataFrame(kwargs)

        if self.validate_data():
            pass

    def validate_data(self):
        """Validate that imported data is in correct format"""
        pass

    def group_data(self):
        self.datecol = self.data.columns[0]
        self.daytypes = {
            "weekday" : [0,1,2,3,4],
            "weekend" : [5,6],
            "holiday" : [7],
            }
        self.dstrules = {}
        self.groupby = {
            "daytype":[self.datecol,get_daytype,self.daytypes],
            "hour":[self.datecol,get_hour,self.dstrules]
            }
        self.columns = self.data.columns[1:]
        self.add_groups()
        if not_valid:
            return Exception

        valid = True
        return valid

    def add_groups(self):
        """Add one or more groups to a Pandas DataFrame"""
        for name, group in self.groupby.items():
            self.data[name] = list(map(lambda x: group[1](x,group[2]),self.data[group[0]]))