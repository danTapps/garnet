"""Const definitions."""

from enum import StrEnum

from homeassistant.const import Platform

DOMAIN = "chefiq"
MFR_ID = 1485

PLATFORMS = [Platform.SENSOR]


class ChefIqTypes(StrEnum):
    """Chef iQ value types."""

    TEMP_MEAT = "temp_meat"
    TEMP_TIP = "temp_tip"
    TEMP_1 = "temp_1"
    TEMP_2 = "temp_2"
    TEMP_3 = "temp_3"
    TEMP_AMBIENT = "temp_ambient"
    BATTERY = "battery"
    NAME = "name"
