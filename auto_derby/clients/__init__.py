from .client import Client, _legacy_current, _legacy_set_current
from .dmm import DMMClient
from .adb import ADBClient

# DEPRECATED

globals()["current"] = _legacy_current
globals()["set_current"] = _legacy_set_current
