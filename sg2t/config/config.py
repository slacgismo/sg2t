"""
Functions for loading configs
"""

import os
import ast
import configparser
from pathlib import Path

def load_config(name=None):
    """Load .ini config file and return as dict.
    The file should be either in the package config src dir (sg2t.config) if
    it's a default file, or in the root config dir (os.environ["SG2T_CONFIG"].

    PARAMETERS
    ----------
    name : str
        Name of config file to load.

    RETURNS
    -------
    config : dict
        Config dict if found.
    """
    if not name:
        name = "config.ini"
    parent_path = Path(__file__).parent.parent
    config_filepath = (
            parent_path / "config" / f"{name}"
    )

    if not os.path.exists(config_filepath):
        # load from env dir if can't be found in package base
        config_dir = os.environ["SG2T_CONFIG"]

        config_env_filepath = (
                config_dir + f"/{name}"
        )

        if not os.path.exists(config_env_filepath):
            raise FileNotFoundError(f"Config file not found in\n" \
                                    f"pkg src dir: {config_filepath}\n" \
                                    f"config dir: {config_env_filepath}\n" \
                                    f"Make sure config file is one of these directories."
                                    )


    ini = configparser.ConfigParser()
    ini.read(config_filepath)

    config = {}
    for section in ini.sections():
        config[section] = {}
        for option in ini.options(section):
            config[section][option] = ast.literal_eval(ini.get(section, option))

    return config

