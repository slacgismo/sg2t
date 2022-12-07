"""This is the base class for defining
a 'io.type.Class' for a given data structure. """
import os
import json
import datetime
import pandas as pd

from sg2t.config import load_config


class IOBase:
    """io base class for defining data structures/sources
    At initialization:
        - load config, if any
        - filename = None

    Methods:
        - get_data (takes filename from user)
        - export_data (takes format from user)
    """
    def __init__(self,
                 config_name: str,
                 config_key: str,
                 metadata_file: str):
        self.data_filename = None
        self.data = None
        self.config = self.load_config(config_name, config_key)
        self.metadata_file = metadata_file
        self.metadata = self.load_metadata(self.metadata_file)

    def load_config(self, config_name=None, key=None):
            """Load TMY3 configuration
            PARAMETERS:
                pathname (str)    Pathname of the configuration file to load
            RETURNS:
                (dict)            Configuration data loaded
            """
            if not config_name and not key:
                pass
            if not config_name:
                # Take default config file
                config_name = "config.ini"
            # Load config
            config = load_config(name=config_name)
            if key:
                try:
                    return config[key]
                except KeyError:
                    raise KeyError(f"No key defined in {config_name} for this data.")
            return None
    
    def load_metadata(self, filename=None):
        """Need to have this file """
        with open(filename) as f:
            # Return metadata dict
           return json.load(f)

    def get_data(self, filename=None):
        self.data_filename = filename if filename else self.data_filename
        if not self.data_filename or not os.path.exists(self.data_filename):
            raise FileNotFoundError(f'File not found: {self.data_filename}')

        # Add source filename to metadata
        self.metadata["filename"] = self.data_filename
        # Data should preferably be loaded with pandas
        self.data = pd.read_table(self.data_filename)

        # Returned data has to be a pd.DataFrame
        return self.data

    def export_data(self,
                    type="CSV",
                    columns=None,
                    filename=None):
        if type=="CSV":
            timestamp = (datetime.datetime.now()).strftime("%Y-%m-%d_%H-%M-%S-%f")
            if not filename:
                filename = f"sg2t_base_data_{timestamp}"
            else:
                filename = filename + "_" + timestamp
            self.data.to_csv(filename, columns=columns)
            # Save metadata as well
            # TODO: adjust metadata to only include info about saved columns, or keep all?
            with open(f"sg2t_base_metadata_{timestamp}.json", "w") as outfile:
                json.dump(self.metadata, outfile)
        else:
            raise NotImplementedError("Only saving to CSV format currently supported.")
