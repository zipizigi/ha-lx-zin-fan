"""Constants for the LX Z:in Fan integration."""

from enum import Enum

DOMAIN = "lx_zin_fan"


class Preset(Enum):
    """Fan Preset."""

    FORCE_OUT = 1
    AUTO = 2
    TURBO = 3
    SLEEP = 4
    FAN = 5
    FORCE_IN = 6
