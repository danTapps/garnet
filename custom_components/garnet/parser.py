"""Garnet parser."""

from __future__ import annotations

import logging
from struct import unpack

from bluetooth_data_tools import short_address
from bluetooth_sensor_state_data import BluetoothData  # type: ignore  # noqa: PGH003
from home_assistant_bluetooth import BluetoothServiceInfo

from .const import MFR_ID_BTP3, MFR_ID_BTP7, GarnetTypes

_LOGGER = logging.getLogger(__name__)


class GarnetBluetoothDeviceData(BluetoothData):
    """Date update for Garnet Bluetooth devices."""

    def __init__(self) -> None:
        """Init members."""

        self.address: str = None
        self.manufacturer = "Garnet"
        self.model = "709-BT"
        self.device_id = None
        super().__init__()

    def _start_update(self, data: BluetoothServiceInfo) -> None:
        """Update from BLE advertisement data."""
        _LOGGER.debug("Parsing Garnet BLE advertisement data: %s", data)

        self.address = data.address

        if MFR_ID_BTP3 in data.manufacturer_data:
            self.model = "709-BTP3"
            manufacturer_data = data.manufacturer_data
            data_bytes = manufacturer_data[MFR_ID_BTP3]
            msg_length = len(data_bytes)
            if msg_length == 14:
                self._process_update_btp3(data_bytes)

        if MFR_ID_BTP7 in data.manufacturer_data:
            self.model = "709-BTP7"
            manufacturer_data = data.manufacturer_data
            data_bytes = manufacturer_data[MFR_ID_BTP7]
            msg_length = len(data_bytes)
            if msg_length == 14:
                self._process_update_btp7(data_bytes)

        self.set_title(
            f"{self.manufacturer} {self.model} {short_address(self.address)}"
        )
        self.set_device_name(
            f"{self.manufacturer} {self.model} {short_address(self.address)}"
        )
        self.set_device_type(self.model)
        self.set_device_manufacturer(self.manufacturer)

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

    def _process_update_btp3(self, data: bytes) -> None:
        """Update from BLE advertisement data."""
        _LOGGER.debug("Got btp3 data %s len %d", format(data), len(data))
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
        if 6 < sensor_type < 11:
            sensor_measurement_unit = "DEGREE"
            sensor_device_class = "TEMPERATURE"

        self.update_sensor(
            key=self._get_sensor_name(sensor_type),
            native_unit_of_measurement=sensor_measurement_unit,
            native_value=sensor_value if sensor_available is True else None,
            device_class=sensor_device_class,
        )

    def _process_update_btp7(self, data: bytes) -> None:
        """Update from BLE advertisement data."""
        _LOGGER.debug("Got btp7 data %s len %d", format(data), len(data))

        (
            coach_id,
            fresh_1,
            grey_1,
            black_1,
            fresh_2,
            grey_2,
            black_2,
            unk_4,
            unk_5,
            voltage,
            unk_6,
            unk_7,
        ) = unpack("<HxBBBBBBBBBBB", data)

        #        coach_id = int.from_bytes(coach_id, byteorder="little")
        #        sensor_type = int.from_bytes(sensor_type, byteorder="little")
        #        sensor_value = sensor_value.decode("utf-8")
        #        sensor_measurement_unit = "%"
        #        sensor_available = True

        _LOGGER.debug(
            "Got coach_id %d fresh1 %d, grey1 %d, black1 %d, fresh2 %d, grey2 %d, black2 %d, voltage %d",
            coach_id,
            fresh_1,
            grey_1,
            black_1,
            fresh_2,
            grey_2,
            black_2,
            voltage,
        )

        self.update_sensor(
            key=GarnetTypes.GREY_TANK,
            native_unit_of_measurement="%",
            native_value=grey_1 if (grey_1 not in {110, 102}) else None,
        )

        self.update_sensor(
            key=GarnetTypes.GREY_TANK2,
            native_unit_of_measurement="%",
            native_value=grey_2 if (grey_2 not in {110, 102}) else None,
        )
        #        self.update_sensor(
        #            key=GarnetTypes.GREY_TANK3,
        #            native_unit_of_measurement="%",
        #            native_value=grey_3 if (grey_2 not in {110, 102}) else None,
        #        )

        self.update_sensor(
            key=GarnetTypes.FRESH_TANK,
            native_unit_of_measurement="%",
            native_value=fresh_1 if (fresh_1 not in {110, 102}) else None,
        )

        self.update_sensor(
            key=GarnetTypes.FRESH_TANK2,
            native_unit_of_measurement="%",
            native_value=fresh_2 if (fresh_2 not in {110, 102}) else None,
        )

        self.update_sensor(
            key=GarnetTypes.BLACK_TANK,
            native_unit_of_measurement="%",
            native_value=black_1 if (black_1 not in {110, 102}) else None,
        )

        self.update_sensor(
            key=GarnetTypes.BLACK_TANK2,
            native_unit_of_measurement="%",
            native_value=black_2 if (black_2 not in {110, 102}) else None,
        )

        self.update_sensor(
            key=GarnetTypes.BATTERY,
            native_unit_of_measurement="V",
            native_value=round(voltage / 10, 2),
            device_class="VOLTAGE",
        )
