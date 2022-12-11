""" This module contains functions to determine where configuration and
data/cache files used by sg2t should be placed.
"""

import os


def _find_home():
    """Locates and return the home directory on system.
    Based on https://github.com/astropy/.

    Returns
    ------
    homdir : str
         The absolute path to the home directory.

    Raises
    ------
    OSError
        If the home directory cannot be located - usually means you are running
        on some platform that doesn't have standard home directories.
    """
    try:
        homedir = os.path.expanduser("~")
    except Exception:
        # Linux, Unix, AIX, OS X
        if os.name == "posix":
            if "HOME" in os.environ:
                homedir = os.environ["HOME"]
            else:
                raise OSError(
                    "Could not find unix home directory to search for "
                    "astropy config dir"
                )
        elif os.name == "nt":  # This is for all modern Windows (NT or after)
            if "MSYSTEM" in os.environ and os.environ.get("HOME"):
                # Likely using an msys shell; use whatever it is using for its
                # $HOME directory
                homedir = os.environ["HOME"]
            # See if there's a local home
            elif "HOMEDRIVE" in os.environ and "HOMEPATH" in os.environ:
                homedir = os.path.join(os.environ["HOMEDRIVE"], os.environ["HOMEPATH"])
            # Maybe a user profile?
            elif "USERPROFILE" in os.environ:
                homedir = os.path.join(os.environ["USERPROFILE"])
            else:
                try:
                    import winreg as wreg

                    shell_folders = r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"
                    key = wreg.OpenKey(wreg.HKEY_CURRENT_USER, shell_folders)

                    homedir = wreg.QueryValueEx(key, "Personal")[0]
                    key.Close()
                except Exception:
                    # As a final possible resort, see if HOME is present
                    if "HOME" in os.environ:
                        homedir = os.environ["HOME"]
                    else:
                        raise OSError(
                            "Could not find windows home directory to "
                            "search for astropy config dir"
                        )
        else:
            # for other platforms, try HOME, although it probably isn't there
            if "HOME" in os.environ:
                homedir = os.environ["HOME"]
            else:
                raise OSError(
                    "Could not find a home directory to search for "
                    "astropy config dir - are you on an unsupported "
                    "platform?"
                )
    return homedir

def get_config_dir(rootname="sg2t"):
    """Determines the package configuration directory name and creates the
    directory if it doesn't exist.
    This directory is ``$HOME/.sg2t/config``.

    Parameters
    ----------
    rootname : str
        Name of the root configuration directory.

    Returns
    -------
    configdir : str
        The absolute path to the configuration directory.
    """
    return os.path.abspath(_find_or_create_root_dir("config", rootname))

def get_cache_dir(rootname="sg2t"):
    """Determines the sg2t cache directory name and creates the directory if it
    doesn't exist.
    This directory is ``$HOME/.sg2t/cache``.

    Parameters
    ----------
    rootname : str
        Name of the root cache directory.

    Returns
    -------
    maindir : str
        The absolute path to the cache subdirectory.
    """
    return os.path.abspath(_find_or_create_root_dir("cache", rootname))

def _find_or_create_root_dir(dirnm, pkgname="sg2t"):
    """Finds package cache subdirectory or creates it if it doesn't exist.

    Parameters
    ----------
    dirnm : str
        Name of the subdirectory.

    pkgname : str
        Name of the root package directory.

    Returns
    -------
    cachedir : str
        The absolute path to the cache directory.
    """
    innerdir = os.path.join(_find_home(), f".{pkgname}")
    maindir = os.path.join(_find_home(), f".{pkgname}", dirnm)

    if not os.path.exists(maindir):
        # first create .sg2t dir if needed
        if not os.path.exists(innerdir):
            try:
                os.mkdir(innerdir)
            except OSError:
                if not os.path.isdir(innerdir):
                    raise
        elif not os.path.isdir(innerdir):
            raise OSError(
                f"Intended {pkgname} {dirnm} directory {maindir} is actually a file."
            )

        try:
            os.mkdir(maindir)
        except OSError:
            if not os.path.isdir(maindir):
                raise

    elif not os.path.isdir(maindir):
        raise OSError(
            f"Intended {pkgname} {dirnm} directory {maindir} is actually a file."
        )

    return os.path.abspath(maindir)