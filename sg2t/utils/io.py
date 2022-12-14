"""This module contains utility functions for I/O actions in sg2t"""

import json
from sg2t.io.schemas import metadata_schema


def load_metadata(filename=None):
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
    if not filename:
        print("No existing metadata found.")
        keys = list(metadata_schema["properties"].keys())
        metadata = {x: {} for x in keys}
        return metadata

    with open(filename) as f:
        # Return metadata dict
        return json.load(f)