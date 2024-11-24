"""Const definitions."""
from enum import StrEnum

from homeassistant.const import Platform

DOMAIN = "garnet"

PLATFORMS = [Platform.SENSOR]


class GarnetTypes(StrEnum):
    """Garnet value types."""

    FRESH_TANK="fresh_tank"
    BLACK_TANK="black_tank"
    GREY_TANK="grey_tank"
    LPG_TANK="lpg_tank"
    LPG_2_TANK="lpg_2_tank"
    GALLEY_TANK="galley_tank"
    GALLEY_2_TANK="galley_2_tank"
    TEMP="temp"
    TEMP_2="temp_2"
    TEMP_3="temp_3"
    TEMP_4="temp_4"
    CHEMICAL_TANK="chemical_tank"
    CHEMICAL_2_TANK="chemical_2_tank"
    BATTERY="battery"

