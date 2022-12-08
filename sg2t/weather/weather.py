"""This is the main class for working with weather data."""
import os
import json
import datetime
import pandas as pd

from sg2t.config import load_config


class Weather:
    """Weather class for working with weather data.
    At initialization:
        - load config, if any
        - filename = None

    Methods:
        - import_data (takes filename from user)
        - get_heat_index
        - plot
        - export
    """
    def __init__(self,
                 config_name: str,
                 config_key: str,
                 metadata_file: str):

        pass