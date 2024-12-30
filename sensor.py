"""Support for Garnet sensors."""

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
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.sensor import sensor_device_info_to_hass_device_info

from .const import DOMAIN, GarnetTypes
from .device import device_key_to_bluetooth_entity_key

_LOGGER = logging.getLogger(__name__)

SENSOR_DESCRIPTIONS = {
    GarnetTypes.FRESH_TANK: SensorEntityDescription(
        key=GarnetTypes.FRESH_TANK,
        device_class=None,
        native_unit_of_measurement="%",
    ),
    GarnetTypes.BLACK_TANK: SensorEntityDescription(
        key=GarnetTypes.BLACK_TANK,
        device_class=None,
        native_unit_of_measurement="%",
    ),
    GarnetTypes.GREY_TANK: SensorEntityDescription(
        key=GarnetTypes.GREY_TANK,
        device_class=None,
        native_unit_of_measurement="%",
    ),
    GarnetTypes.LPG_TANK: SensorEntityDescription(
        key=GarnetTypes.LPG_TANK,
        device_class=None,
        native_unit_of_measurement="%",
    ),
    GarnetTypes.BATTERY: SensorEntityDescription(
        key=GarnetTypes.BATTERY,
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement="V",
    ),
    "signal_strength": SensorEntityDescription(
        key="signal_strength_dBm",
        device_class="signal_strength",
        native_unit_of_measurement="dBm",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    GarnetTypes.LPG_2_TANK: SensorEntityDescription(
        key=GarnetTypes.LPG_2_TANK,
        device_class=None,
        native_unit_of_measurement="%",
    ),
    GarnetTypes.GALLEY_TANK: SensorEntityDescription(
        key=GarnetTypes.GALLEY_TANK,
        device_class=None,
        native_unit_of_measurement="%",
    ),
    GarnetTypes.GALLEY_2_TANK: SensorEntityDescription(
        key=GarnetTypes.GALLEY_2_TANK,
        device_class=None,
        native_unit_of_measurement="%",
    ),
    GarnetTypes.TEMP: SensorEntityDescription(
        key=GarnetTypes.TEMP,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement="",
    ),
    GarnetTypes.TEMP_2: SensorEntityDescription(
        key=GarnetTypes.TEMP_2,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement="",
    ),
    GarnetTypes.TEMP_3: SensorEntityDescription(
        key=GarnetTypes.TEMP_3,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement="",
    ),
    GarnetTypes.TEMP_4: SensorEntityDescription(
        key=GarnetTypes.TEMP_4,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement="",
    ),
    GarnetTypes.CHEMICAL_TANK: SensorEntityDescription(
        key=GarnetTypes.CHEMICAL_TANK,
        device_class=None,
        native_unit_of_measurement="%",
    ),
    GarnetTypes.CHEMICAL_2_TANK: SensorEntityDescription(
        key=GarnetTypes.CHEMICAL_2_TANK,
        device_class=None,
        native_unit_of_measurement="%",
    ),
}


def sensor_update_to_bluetooth_data_update(sensor_update) -> PassiveBluetoothDataUpdate:
    """Convert a sensor update to a bluetooth data update."""
    _LOGGER.debug(sensor_update)
    return PassiveBluetoothDataUpdate(
        devices={
            device_id: sensor_device_info_to_hass_device_info(device_info)
            for device_id, device_info in sensor_update.devices.items()
        },
        entity_descriptions={
            device_key_to_bluetooth_entity_key(device_key): SENSOR_DESCRIPTIONS[
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
    """Set up the Garnet BLE sensors."""
    coordinator: PassiveBluetoothProcessorCoordinator = hass.data[DOMAIN][
        entry.entry_id
    ]
    processor = PassiveBluetoothDataProcessor(sensor_update_to_bluetooth_data_update)
    entry.async_on_unload(
        processor.async_add_entities_listener(
            GarnetBluetoothSensorEntity, async_add_entities
        )
    )
    entry.async_on_unload(coordinator.async_register_processor(processor))


class GarnetBluetoothSensorEntity(
    PassiveBluetoothProcessorEntity[
        PassiveBluetoothDataProcessor[Optional[Union[float, int]], 1]  # noqa: UP007
    ],
    SensorEntity,
):
    """Representation of a Garnet sensor."""

    @property
    def native_value(self) -> int | float | None:
        """Return the native value."""
        return self.processor.entity_data.get(self.entity_key)
