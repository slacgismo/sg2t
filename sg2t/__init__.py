# Licensed under a 3-clause BSD style license - see LICENSE.rst
import os
from sg2t.config.paths import get_cache_dir, get_config_dir

package_dir = os.path.abspath(__file__ + "/../")
cache_dir = get_cache_dir()
config_dir =  get_config_dir()

os.environ["SG2T_HOME"] = package_dir
os.environ["SG2T_CACHE"] = cache_dir
os.environ["SG2T_CONFIG"] = config_dir