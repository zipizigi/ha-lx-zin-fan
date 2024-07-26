"""Support for Naver Weather Sensors."""

import logging
from typing import Any, cast

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity

from .zin_api import LXZinApi, LXZinInfo

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry[LXZinApi],
    async_add_entities: list[Entity],
) -> None:
    """Set up fan."""

    api = cast(LXZinApi, config_entry.runtime_data)
    async_add_entities(
        [
            ZinSensorEntity(
                "TVOCs",
                "tvoc",
                api,
                SensorDeviceClass.AQI,
                None,
                "tvoc",
            ),
            ZinSensorEntity(
                "온도",
                "temp",
                api,
                SensorDeviceClass.TEMPERATURE,
                "°C",
                "temperature",
            ),
            ZinSensorEntity(
                "습도",
                "humi",
                api,
                SensorDeviceClass.HUMIDITY,
                "%",
                "humidity",
            ),
            ZinSensorEntity(
                "CO2",
                "co2",
                api,
                SensorDeviceClass.CO2,
                "ppm",
                "co2",
            ),
            ZinSensorEntity(
                "초미세먼지(PM2.5)",
                "pm25",
                api,
                SensorDeviceClass.PM25,
                "µg/m³",
                "pm25",
            ),
            ZinSensorEntity(
                "전열소자",
                "heatlife",
                api,
                SensorDeviceClass.BATTERY,
                "%",
                "heatExchanger",
            ),
            ZinSensorEntity(
                "필터",
                "filter",
                api,
                SensorDeviceClass.BATTERY,
                "%",
                "filter",
            ),
            ZinSensorEntity(
                "갱신 시간",
                "updated",
                api,
                SensorDeviceClass.TIMESTAMP,
                None,
                "lastUpdated",
                None,
                True,
            ),
        ]
    )


class ZinSensorEntity(SensorEntity):
    """Zin Sensor Entity."""

    def __init__(
        self,
        nameSuffix: str,
        idSuffix: str,
        api: LXZinApi,
        deviceClass: SensorDeviceClass,
        unit: str,
        infoKey: str,
        stateClass: str = "measurement",
        isRecord: bool = True,
    ) -> None:
        """Initialize the fan."""
        self.api = api
        self.nameSuffix = nameSuffix
        self.idSuffix = idSuffix
        self.info: LXZinInfo = api.data
        self.deviceClass: SensorDeviceClass = deviceClass
        self.unit = unit
        self.infoKey = infoKey
        self.stateClass = stateClass
        self.isRecord = isRecord

    @property
    def unique_id(self) -> str:
        """Get unique ID."""
        return self.api.deviceId + "-" + self.idSuffix

    @property
    def device_class(self) -> SensorDeviceClass:
        """Get device class."""
        return self.deviceClass

    @property
    def native_unit_of_measurement(self) -> str:
        """Get unit."""
        return self.unit

    @property
    def native_value(self) -> Any:
        """Get native value."""
        return self.info[self.infoKey] if self.info is not None else None

    @property
    def state_class(self) -> str | None:
        """Return state class."""
        return self.stateClass

    @property
    def device_info(self) -> DeviceInfo | None:
        """Get device info."""
        return self.info.deviceInfo if self.info is not None else None

    @property
    def entity_registry_enabled_default(self) -> bool:
        """Get registry enabled."""
        return self.isRecord

    @property
    def name(self) -> str | None:
        """Return the name of the fan."""
        return self.info.name + " " + self.nameSuffix if self.info is not None else None

    @property
    def should_poll(self) -> bool:
        """Polling needed for this device."""
        return True

    def update(self) -> None:
        """Fetch new state data for the fan."""
        self.info = self.api.data
