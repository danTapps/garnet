"""Support for Garnet devices."""

from __future__ import annotations

import logging

from sensor_state_data import DeviceKey  # type: ignore  # noqa: PGH003

from homeassistant.components.bluetooth.passive_update_processor import (
    PassiveBluetoothEntityKey,
)

_LOGGER = logging.getLogger(__name__)


def device_key_to_bluetooth_entity_key(
    device_key: DeviceKey,
) -> PassiveBluetoothEntityKey:
    """Convert a device key to an entity key."""
    return PassiveBluetoothEntityKey(device_key.key, device_key.device_id)
