"""Chef iQ parser."""

from __future__ import annotations

import logging
from struct import unpack

from bluetooth_data_tools import short_address
from bluetooth_sensor_state_data import BluetoothData  # type: ignore  # noqa: PGH003
from home_assistant_bluetooth import BluetoothServiceInfo

from homeassistant.const import UnitOfTemperature

from .const import MFR_ID, ChefIqTypes

_LOGGER = logging.getLogger(__name__)


class ChefIqBluetoothDeviceData(BluetoothData):
    """Date update for Chef iQ Bluetooth devices."""

    def __init__(self) -> None:
        """Init members."""

        self.address: str = None
        self.manufacturer = "Chef iQ"
        self.model = "CQ60"
        self.device_id = None
        super().__init__()

    def _start_update(self, data: BluetoothServiceInfo) -> None:
        """Update from BLE advertisement data."""

        # _LOGGER.debug(
        #    "Parsing Chef iQ BLE advertisement MFR_ID %s",
        #    "".join(f"0x{byte:02x} " for byte in data.manufacturer_data),
        # )

        if MFR_ID not in data.manufacturer_data:
            return
        manufacturer_data = data.manufacturer_data
        msg_data = manufacturer_data[MFR_ID]
        msg_length = len(msg_data)

        _LOGGER.debug(
            "Parsing Chef iQ BLE advertisement data len: %d, data: %s",
            msg_length,
            "".join(f"0x{byte:02x} " for byte in msg_data),
        )
        _LOGGER.debug(msg_data)

        if msg_length == 0:
            return

        msg_type = msg_data[0]

        if not (
            (msg_length == 18 and msg_type == 1)
            or (msg_length == 16 and msg_type == 0)
            or (msg_length == 17 and msg_type == 3)
        ):
            return

        self.address = data.address

        self.set_title(
            f"{self.manufacturer} {self.model} {short_address(self.address)}"
        )
        self.set_device_name(
            f"{self.manufacturer} {self.model} {short_address(self.address)}"
        )
        self.set_device_type(self.model)
        self.set_device_manufacturer(self.manufacturer)

        if msg_type == 1:
            self._process_update(msg_data)
        #        elif msg_type == 0:
        #            self._process_name(msg_data)
        elif msg_type == 3:
            self._process_status(msg_data)

    def _process_update(self, data: bytes) -> None:
        """Update from BLE advertisement data."""
        # _LOGGER.debug("Got data %s len %d", format(data), len(data))

        (
            msg_type,
            _,
            temp_probe_3,
            temp_meat,
            temp_tip,
            temp_probe_1,
            temp_probe_2,
            _,
            temp_ambient,
            _,
        ) = unpack("<BBHHHHHHHH", data)

        if msg_type != 1:
            return

        self.update_sensor(
            key=ChefIqTypes.TEMP_3,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            native_value=temp_probe_3 / 10,
            device_class="TEMPERATURE",
        )

        self.update_sensor(
            key=ChefIqTypes.TEMP_MEAT,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            native_value=temp_meat / 10,
            device_class="TEMPERATURE",
        )

        self.update_sensor(
            key=ChefIqTypes.TEMP_TIP,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            native_value=temp_tip / 10,
            device_class="TEMPERATURE",
        )

        self.update_sensor(
            key=ChefIqTypes.TEMP_1,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            native_value=temp_probe_1 / 10,
            device_class="TEMPERATURE",
        )

        self.update_sensor(
            key=ChefIqTypes.TEMP_2,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            native_value=temp_probe_2 / 10,
            device_class="TEMPERATURE",
        )

        self.update_sensor(
            key=ChefIqTypes.TEMP_AMBIENT,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            native_value=temp_ambient / 10,
            device_class="TEMPERATURE",
        )

    def _process_name(self, data: bytes) -> None:
        """Update from BLE advertisement data."""
        # _LOGGER.debug("Got data %s len %d", format(data), len(data))

        name: str = ""
        (
            msg_type,
            _,
            name,
            _,
        ) = unpack("<BB12sH", data)

        _LOGGER.debug("Got name %s", name)

    def _process_status(self, data: bytes) -> None:
        """Update from BLE advertisement data."""
        # _LOGGER.debug("Got data %s len %d", format(data), len(data))

        (
            msg_type,
            _,
            _,
            _,
            _,
            _,
            _,
            _,
            battery,
            _,
            _,
            _,
            _,
            _,
            _,
            _,
        ) = unpack("<BBBBBBBBBBBBBBBH", data)

        self.update_sensor(
            key=ChefIqTypes.BATTERY,
            native_unit_of_measurement="PERCENT",
            native_value=battery,
            device_class="BATTERY",
        )
