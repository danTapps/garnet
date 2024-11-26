"""Garnet parser."""

from __future__ import annotations

import logging
from struct import unpack

from bluetooth_data_tools import short_address
from bluetooth_sensor_state_data import BluetoothData  # type: ignore  # noqa: PGH003
from home_assistant_bluetooth import BluetoothServiceInfo

from .const import GarnetTypes

_LOGGER = logging.getLogger(__name__)

MFR_ID = 305


class GarnetBluetoothDeviceData(BluetoothData):
    """Date update for Garnet Bluetooth devices."""

    def __init__(self) -> None:
        """Init members."""

        self.address: str = None
        self.manufacturer = "Garnet"
        self.model = "709-BT"
        self.device_id = None
        super().__init__()

    def _start_update(self, service_info: BluetoothServiceInfo) -> None:
        """Update from BLE advertisement data."""
        _LOGGER.debug("Parsing Garnet BLE advertisement data: %s", service_info)
        if MFR_ID not in service_info.manufacturer_data:
            return
        manufacturer_data = service_info.manufacturer_data
        data = manufacturer_data[MFR_ID]
        msg_length = len(data)
        if msg_length != 14:
            return

        self.address = service_info.address

        self.set_title(
            f"{self.manufacturer} {self.model} {short_address(self.address)}"
        )
        self.set_device_name(
            f"{self.manufacturer} {self.model} {short_address(self.address)}"
        )
        self.set_device_type(self.model)
        self.set_device_manufacturer(self.manufacturer)

        self._process_update(data)

    # 0 = Fresh
    # 1 = Black
    # 2 = Gray
    # 3 = LPG
    # 4 = LPG 2
    # 5 = Galley
    # 6 = Galley 2
    # 7 = Temp
    # 8 = Temp 2
    # 9 = Temp 3
    # 10 = Temp 4
    # 11 = Chemical
    # 12 = Chemical 2
    # 13 = Battery x 10

    def _get_sensor_name(self, sensor_type):
        if sensor_type == 0:
            return GarnetTypes.FRESH_TANK
        if sensor_type == 1:
            return GarnetTypes.BLACK_TANK
        if sensor_type == 2:
            return GarnetTypes.GREY_TANK
        if sensor_type == 3:
            return GarnetTypes.LPG_TANK
        if sensor_type == 4:
            return GarnetTypes.LPG_2_TANK
        if sensor_type == 5:
            return GarnetTypes.GALLEY_TANK
        if sensor_type == 6:
            return GarnetTypes.GALLEY_2_TANK
        if sensor_type == 7:
            return GarnetTypes.TEMP
        if sensor_type == 8:
            return GarnetTypes.TEMP_2
        if sensor_type == 9:
            return GarnetTypes.TEMP_3
        if sensor_type == 10:
            return GarnetTypes.TEMP_4
        if sensor_type == 11:
            return GarnetTypes.CHEMICAL_TANK
        if sensor_type == 12:
            return GarnetTypes.CHEMICAL_2_TANK
        if sensor_type == 13:
            return GarnetTypes.BATTERY

        return f"unknown_{sensor_type}"

    def _process_update(self, data: bytes) -> None:
        """Update from BLE advertisement data."""
        _LOGGER.debug("Got data %s len %d", format(data), len(data))
        (coach_id, sensor_type, sensor_value, sensor_volume, sensor_total, alarm) = (
            unpack("@3sc3s3s3sc", data)
        )

        coach_id = int.from_bytes(coach_id, byteorder="little")
        sensor_type = int.from_bytes(sensor_type, byteorder="little")
        sensor_value = sensor_value.decode("utf-8")
        sensor_measurement_unit = "%"
        sensor_available = True

        _LOGGER.debug(
            "Got coach_id %d sensor_type %d sensor_value %s",
            coach_id,
            sensor_type,
            format(sensor_value),
        )
        if sensor_type == 255:
            _LOGGER.debug("System booting up, skip update")
            return
        if sensor_value in ("OPN", "NBO"):
            _LOGGER.info(
                "Sensor %s is %s, no update",
                self._get_sensor_name(sensor_type),
                format(sensor_value),
            )
            sensor_available = False
        #            return
        if sensor_available is True:
            try:
                sensor_value = int(sensor_value)
            except Exception:  # noqa: BLE001
                sensor_available = False
        sensor_device_class = None
        if sensor_type == 13:
            sensor_value = round(sensor_value / 10, 2)
            sensor_measurement_unit = "V"
            sensor_device_class = "VOLTAGE"
        if sensor_type >= 7 and sensor_type <= 10:
            sensor_measurement_unit = "DEGREE"
            sensor_device_class = "TEMPERATURE"

        self.update_sensor(
            key=self._get_sensor_name(sensor_type),
            native_unit_of_measurement=sensor_measurement_unit,
            native_value=sensor_value if sensor_available is True else None,
            device_class=sensor_device_class,
        )


#        else:
#            self.update_sensor(
#                key=self._get_sensor_name(sensor_type),
#                native_unit_of_measurement=sensor_measurement_unit,
#                device_class=sensor_device_class,
#                available=sensor_available,
#            )
