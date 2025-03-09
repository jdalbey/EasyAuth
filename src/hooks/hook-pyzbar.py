import os
import sys
import ctypes.util
""" pyinstaller runtime-hook for pyzbar.
 Background: pyzbar wants to load libzbar.so.0 from the /usr directory.  
 However, if the user hasn't installed it, find_library() will fail.
 So this hook points the library path to pyinstaller's internal directory."""

# Determine which mode PyInstaller bundled the application
if hasattr(sys, "_MEIPASS"):
    # Running from PyInstaller onefile bundle
    lib_path = os.path.join(sys._MEIPASS, "libzbar.so.0")
else:
    # Running in a normal environment (or without --onefile)
    lib_path = os.path.join(os.path.dirname(__file__), "_internal", "libzbar.so.0")

# Set LD_LIBRARY_PATH so find_library() might work
os.environ["LD_LIBRARY_PATH"] = os.path.dirname(lib_path) + ":" + os.environ.get("LD_LIBRARY_PATH", "")

# if find_libary doesn't work
if not ctypes.util.find_library("zbar"):
    # Manually load the library
    ctypes.CDLL(lib_path, ctypes.RTLD_GLOBAL)
