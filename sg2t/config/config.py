"""
Functions for loading configs
"""

import os
import ast
import configparser
from pathlib import Path

def load_config(name=None, verbose=False):
    """Load .ini config file and return as dict
    parameters
    ----------
    name: str
        label of config file to load
    verbose : bool
    """
    if not name:
        name = "config.ini"
    parent_path = Path(__file__).parent.parent
    config_filepath = (
            parent_path / "config" / f"{name}"
    )
    if verbose:
        print(f'Loading config: {config_filepath}')

    if not os.path.exists(config_filepath):
        raise FileNotFoundError(f'Config file not found: {config_filepath}')

    ini = configparser.ConfigParser()
    ini.read(config_filepath)

    config = {}
    for section in ini.sections():
        config[section] = {}
        for option in ini.options(section):
            config[section][option] = ast.literal_eval(ini.get(section, option))

    return config

# def config_filepath(name='sg2t'):
#     """
#     Return path to config file
#     parameters
#     ----------
#     name : str
#     """
#     if name is None:
#         name = 'sg2t'
#
#     try:
#         sg2t_path = os.environ['SG2T_DIR']
#     except KeyError:
#         raise EnvironmentError('Environment variable SG2T_DIR not set. '
#                                'Set path to code directory, e.g., '
#                                "'export SG2T_DIR=${HOME}/path/to/sg2t'")
#
#     return os.path.join(sg2t_path, 'sg2t', 'config', f'{name}.ini')

