"""This is the base class for defining
a 'io.type.Class' for a given data structure. """
import os
import datetime

import json
import pandas as pd

from sg2t.config import load_config
from sg2t.utils import Timeseries
from sg2t.utils.saving import NpEncoder as NpEncoder
from sg2t.utils.io import load_metadata


class IOBase(Timeseries):
    """I/O base class for defining data structures/sources.
    At initialization:
        - config_name, str, path to config file, if any
        - config_key, str, if config_name given
        - metadata_file, str, path to config file, if any

    Methods:
        - load_config
        - load_metadata
        - get_data (takes filename from user)
        - export (takes format from user)
    """
    def __init__(self,
                 config_name: str,
                 config_key: str,
                 metadata_file: str):
        """ IO object initialization.

        Parameters
        ----------
        config_name : str
            Name of configuration file in sg2t.config or cache directory, optional.

        config_key : str
            Key in config corresponding to this class, required if
            config_name is given.

        metadata_file : str
            Absolute path to JSON file containing the metadata for this
             type of data.
        """
        self.data_filename = None
        self.data = None
        self.config = self.load_config(config_name, config_key)
        self.metadata_file = metadata_file
        self.metadata = self.load_metadata(self.metadata_file)

    def load_config(self, config_name=None, key=None):
        """Load configuration.

        PARAMETERS
        ----------
        config_name : str
            Name of configuration file in sg2t.config, optional.

        key : str
            Key in config corresponding to this class, required if
            config_name is given.

        RETURNS
        -------
        config : dict
            Configuration dict, if any, otherwise None.
        """
        return load_config(config_name, key)
    
    def load_metadata(self, filename=None):
        """Load metadata of dataset.

        PARAMETERS
        ----------
        filename : str
            Full path to metadata file.

        RETURNS
        -------
        metadata : dict
            Metadata dict, if any, otherwise a dict w/ no values
             with keys based on the metadata schema.
        """
        return load_metadata(filename)

    def get_data(self, filename=None):
        """Load data from file into Pandas DataFrame.

        PARAMETERS
        ----------
        filename : str
            Full path to data file.

        RETURNS
        -------
        self.data : pd.DataFrame
            DataFrame of data if it exists.
        """
        self.data_filename = filename if filename else self.data_filename
        if not self.data_filename:
            raise Exception("No data file specified.")
        elif not os.path.exists(self.data_filename):
            raise FileNotFoundError(f'File not found: {self.data_filename}')

        # Add source filename to metadata
        self.metadata["file"]["filename"] = self.data_filename
        try:
            # Data should preferably be loaded with pandas
            self.data = pd.read_table(self.data_filename)
        except:
            raise Exception("File could not be loaded with pandas.")

        return self.data

    def _export(self,
                columns=None,
                type="CSV",
                filename=None):
        """Export data from pd.Daframe into a CSV file or into
        sg2t formatted DataFrame to pass onto sg2t opps.
        If saving to file, the file will be saved in the cache which
        can be accessed through os.environ["SG2T_CACHE"].

        PARAMETERS
        ----------
        columns : list of str
            List of columns to save/export from DataFrame.

        type : str
            Type of file to save data as. Currently only supports CSV.

        filename : str
            Name of output file. It will append a timestamp to that.

        RETURNS
        -------
        out : str
            Out filename and json metadata filename.
        """
        if type=="CSV":
            timestamp = (datetime.datetime.now()).strftime("%Y-%m-%d_%H-%M-%S-%f")[:-4]
            if not filename:
                filename = f"sg2t_base_data_{timestamp}"
                metada_filename = f"sg2t_base_metadata_{timestamp}"
            else:
                filename = filename + "_" + timestamp
                metadata_filename = f"metadata_{filename}"

            cache_dir = os.environ["SG2T_CACHE"]
            filename = os.path.join(cache_dir, filename) + ".csv"
            metadata_filename = os.path.join(cache_dir, metadata_filename) + ".json"

            self.data.to_csv(filename, columns=columns, index=False)
            # Save metadata as well
            with open(metadata_filename, "w") as outfile:
                json.dump(self.metadata, outfile, cls=NpEncoder)

            return filename, metadata_filename
        else:
            raise NotImplementedError("Only saving to CSV format currently supported.")
