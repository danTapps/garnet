"""Support for Chef iQ sensors."""

from __future__ import annotations

import logging
from typing import Optional, Union

from homeassistant import config_entries
from homeassistant.components.bluetooth.passive_update_processor import (
    PassiveBluetoothDataProcessor,
    PassiveBluetoothDataUpdate,
    PassiveBluetoothProcessorCoordinator,
    PassiveBluetoothProcessorEntity,
)
from homeassistant.components.text import TextEntity, TextEntityDescription
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.sensor import sensor_device_info_to_hass_device_info

from .const import DOMAIN, ChefIqTypes
from .device import device_key_to_bluetooth_entity_key

_LOGGER = logging.getLogger(__name__)

TEXT_DESCRIPTIONS = {
    ChefIqTypes.NAME: TextEntityDescription(
        key=ChefIqTypes.NAME,
        entity_category=EntityCategory.CONFIG,
    ),
}


def sensor_update_to_bluetooth_data_update(sensor_update) -> PassiveBluetoothDataUpdate:
    """Convert a sensor update to a bluetooth data update."""

    return PassiveBluetoothDataUpdate(
        devices={
            device_id: sensor_device_info_to_hass_device_info(device_info)
            for device_id, device_info in sensor_update.devices.items()
        },
        entity_descriptions={
            device_key_to_bluetooth_entity_key(device_key): TEXT_DESCRIPTIONS[
                description.device_key.key
            ]
            for device_key, description in sensor_update.entity_descriptions.items()
        },
        entity_data={
            device_key_to_bluetooth_entity_key(device_key): sensor_values.native_value
            for device_key, sensor_values in sensor_update.entity_values.items()
        },
        entity_names={
            device_key_to_bluetooth_entity_key(device_key): sensor_values.name
            for device_key, sensor_values in sensor_update.entity_values.items()
        },
    )


async def async_setup_entry(
    hass: HomeAssistant,
    entry: config_entries.ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Chef iQ BLE sensors."""
    coordinator: PassiveBluetoothProcessorCoordinator = hass.data[DOMAIN][
        entry.entry_id
    ]
    processor = PassiveBluetoothDataProcessor(sensor_update_to_bluetooth_data_update)
    entry.async_on_unload(
        processor.async_add_entities_listener(
            ChefIqBluetoothTextEntity, async_add_entities
        )
    )
    entry.async_on_unload(coordinator.async_register_processor(processor))


class ChefIqBluetoothTextEntity(
    PassiveBluetoothProcessorEntity[
        PassiveBluetoothDataProcessor[Optional[Union[float, int]], 1]  # noqa: UP007
    ],
    TextEntity,
):
    """Representation of a Chef iQ sensor."""

    @property
    def native_value(self) -> int | float | None:
        """Return the native value."""
        return self.processor.entity_data.get(self.entity_key)
