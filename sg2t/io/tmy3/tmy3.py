"""Module for TMY3 data, adapted from  GridLAB-D"""
import os, sys
from pathlib import Path
import json
import pandas
import datetime
import requests
from sg2t.io.tmy3 import converters

package_dir = Path.cwd().parent.parent
cache_dir = f"{package_dir}/weather/data/tmy3"

def load_config(pathname=f"{config_dir}/config.json"):
    """Load TMY3 configuration
    PARAMETERS:
        pathname (str)    Pathname of the configuration file to load
    RETURNS:
        (dict)            Configuration data loaded
    """
    with open(filename,"rt") as f:
        global config
        config = json.load(f)
    return config

def save_config(filename=f"{config_dir}/config.json"):
    """Save TMY3 configuration
    PARAMETERS:
        pathname (str)    Pathname of the configuration file to load
    RETURNS:
        None
    """
    with open(filename,"wt") as f:
        json.dump(config,f,indent=4)

try:
    load_config()
except:
    config = dict(
        server = "https://github.com/",
        organization = "slacgismo",
        repository = "gridlabd-weather",
        branch = "master",
        country = "US",
        index_name = ".index",
        )
    save_config()

if not os.path.exists(cache_dir):
    os.makedirs(cache_dir,exist_ok=True)

def get_index():
    """Get station index
    RETURNS:
        (list) List of station names sorted alphabetically
    """
    return sorted(get_data(config['index_name']).strip().split('\n'))

def get_tmy3(tmy3_name,coerce_year=None):
    """Get station TMY3 data
    PARAMETERS:
        tmy3_name (str)     Station name from station index; see get_index()
        coerce_year (int)   Year to use when indexing dates (default is None, i.e., use TMY data year)
    RETURNS:
        (class TMY3)        TMY3 object
    """
    filename = get_data(tmy3_name,cache_filename_only=True)
    return TMY3(filename,coerce_year)

def get_data(filename,cache_filename_only=False):
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
        with open(cache_file,"rt") as f:
            return f.read()
    url = f"{config['server']}{config['organization']}/{config['repository']}/raw/{config['branch']}/{config['country']}/{filename}"
    r = requests.get(url)
    if r.status_code == 200:
        with open(cache_file,"wt") as f:
            f.write(r.text)
        if cache_filename_only:
            return cache_file
        return r.text
    else:
        raise OSError(2,"file not found",cache_file)

class TMY3:
    """TMY3 container implementation
    """
    def __init__(self,filename,coerce_year=None):
        """TMY3 object initialization
        PARAMETERS:
            filename (str)   Filename of TMY3 data to load
            coerce_year      Year to use when setting dates (default None, i.e., use TMY3 years)
        PROPERTIES:
            alb (pandas.Series)            Alb (unitless) as float
            aod (pandas.Series)            AOD (unitless) as float
            ceilhgt (pandas.Series)        CeilHgt (m) as float
            dataframe (pandas.DataFrame)   Raw TMY3 data
            date (pandas.Series)           Date (MM/DD/YYYY) as datetime.date
            datetime (pandas.Series)       Full date and time index as datetime.datetime
            dewpoint (pandas.Series)       Dew-point (C) as float
            dhi (pandas.Series)            DHI (W/m^2) as float
            dhillum(pandas.Series)         DH illum (lx) as float
            dni (pandas.Series)            DNI (W/m^2) as float
            dnillum (pandas.Series)        DN illum (lx) as float
            drybulb (pandas.Series)        Dry-bulb (C) as float
            ertn (pandas.Series)           ETRN (W/m^2) as float
            etr (pandas.Series)            ETR (W/m^2) as float
            ghi (pandas.Series)            GHI (W/m^2) as float
            ghillum (pandas.Series)        GH illum (lx) as float
            hvis (pandas.Series)           Hvis (m) as float
            lprecipdepth (pandas.Series)   Lprecip depth (mm) as float
            lprecipquantity(pandas.Series) Lprecip quantity (hr)
            opqcld (pandas.Series)         OpqCld (tenths) as float
            pressure (pandas.Series)       Pressure (mbar) as float
            pwat (pandas.Series)           Pwat (cm) as float
            rhum (pandas.Series)           RHum (%) as float
            time (pandas.Series)           Time (HH:MM) as datetime.time
            totcld (pandas.Series)         TotCld (tenths) as float
            units (dict)                   Units dictionary for float properties
            wdir (pandas.Series)           Wdir (degrees) as float
            wspd (pandas.Series)           Wspd (m/s) as float
            zenlu (pandas.Series)          Zenith lum (cd/m^2) as float
        """
        info = pandas.read_table(filename,
            delimiter=",",
            skiprows=0,
            nrows=1,
            header=None,
            names=["station","name","state","tzoffset","latitude","longitude","elevation"])
        for item in info.columns:
            setattr(self,item,info[item])

        self.dataframe = pandas.read_table(filename,delimiter=",",skiprows=1,nrows=8760,header=0,
            converters={

            })
        self.dataframe.index.name = "Hour"
        self.dataframe.insert(0,'DateTime',list(map(lambda x,y: datetime.datetime(x.year,x.month,x.day,y.hour),*(self.dataframe['Date (MM/DD/YYYY)'],self.dataframe['Time (HH:MM)']))))
        for column, name in { get dict from config

        }.items():
            setattr(self,name,self.dataframe[column])
        self.units = { get dict from config

        }