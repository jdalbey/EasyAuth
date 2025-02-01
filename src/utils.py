import os
import sys

""" Utility functions """

def assets_dir():
    """ Return the current path to project assets, depending on development or production environment. """
    base_dir = ""
    # Are we in production mode?
    if getattr(sys, 'frozen', False):
        # PyInstaller bundled case - prefix the temp directory path
        base_dir = sys._MEIPASS  # type: ignore   #--keep PyCharm happy
    # build path from base_dir and filename
    return os.path.join(base_dir, "assets")
