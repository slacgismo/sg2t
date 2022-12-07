"""Module for TMY3 data, adapted from  GridLAB-D"""
import os, sys
import json
import pandas as pd
import datetime
import requests

from sg2t.io.weather.base import IOBase
#from sg2t.io.tmy3 import converters
from sg2t.config import load_config

package_dir = os.path.abspath(__file__ + "/../../../../")
cache_dir = f"{package_dir}/weather/data/tmy3"

if not os.path.exists(cache_dir):
    os.makedirs(cache_dir,exist_ok=True)

class TMY3(IOBase):
    """TMY3 container implementation
    """
    def __init__(self,
                 config_name="config.ini",
                 config_key="data.tmy3",
                 metadata_file=package_dir+"/io/weather/tmy3/"+"tmy3_nrel.json"
                 ):
        """TMY3 object initialization
        PARAMETERS:
            filename (str)   Filename of TMY3 data to load
            coerce_year      Year to use when setting dates (default None, i.e., use TMY3 years)
        """
        super().__init__(config_name,
                         config_key,
                         metadata_file
                         )
    def get_index(self):
        """Get station index
        RETURNS:
            (list) List of station names sorted alphabetically
        """
        index_filename = self.metadata['metadata']['index_name']
        return sorted(self.get_data(index_filename).strip().split('\n'))

#     def get_data(self, filename=None):
#         self.data_filename = filename if filename else self.data_filename
#         if not self.data_filename or not os.path.exists(self.data_filename):
#             raise FileNotFoundError(f'File not found: {self.data_filename}')
#
#         # Add source filename to metadata
#         self.metadata["filename"] = self.data_filename
#         # Data should preferably be loaded with pandas
#         self.data = pd.read_table(self.data_filename)
#
#         # Returned data has to be a pd.DataFrame
#         return self.data
#
#         info = pd.read_table(filename,
#             delimiter=",",
#             skiprows=0,
#             nrows=1,
#             header=None,
#             names=["station","name","state","tzoffset","latitude","longitude","elevation"])
#         for item in info.columns:
#             setattr(self,item,info[item])
#
#         self.dataframe = pd.read_table(filename,delimiter=",",skiprows=1,nrows=8760,header=0,
#             converters={
#
#             })
#         self.dataframe.index.name = "Hour"
#         self.dataframe.insert(0,'DateTime',
#                               list(map(lambda x,y: datetime.datetime(x.year,x.month,x.day,y.hour),
#                                        *(self.dataframe['Date (MM/DD/YYYY)'],
#                                          self.dataframe['Time (HH:MM)']))))
#         # for column, name in { get dict from config
#         #
#         # }.items():
#         #     setattr(self,name,self.dataframe[column])
#         # self.units = { get dict from config
#         #
#         # }
# \

    def get_data(self, filename, cache_filename_only=False):
        """Get raw TMY3 data file
        PARAMETERS:
            filename (str)               TMY3 data file to retrieve from
            cache_filename_only (bool)   Return only the name of the cache file, not the data in the file
        RETURNS:
            (class TMY3) or (str)        TMY3 data or cache file name
        """
        cache_file = f"{cache_dir}/{filename}"
        if os.path.exists(cache_file):
            if cache_filename_only:
                return cache_file
            with open(cache_file, "rt") as f:
                # this works print(f.read())
                return f.read()

        url = f"{self.config['server']}" \
              f"{self.config['organization']}" \
              f"/{self.config['repository']}/raw/" \
              f"{self.config['branch']}/" \
              f"{self.config['country']}/{filename}"

        r = requests.get(url)
        if r.status_code == 200:
            with open(cache_file, "wt") as f:
                f.write(r.text)
            if cache_filename_only:
                return cache_file
            return r.text
        else:
            raise OSError(2, "file not found", cache_file)
