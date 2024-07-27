"""Support for Naver Weather Sensors."""

import logging
import math
from typing import Any, Optional, cast
import time

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity
from homeassistant.util.percentage import (
    int_states_in_range,
    percentage_to_ranged_value,
    ranged_value_to_percentage,
)

from .const import Preset
from .zin_api import LXZinApi, LXZinInfo

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry[LXZinApi],
    async_add_entities: list[Entity],
) -> None:
    """Set up fan."""

    api = cast(LXZinApi, config_entry.runtime_data)
    async_add_entities([ZinFanEntity(api)])


class ZinFanEntity(FanEntity):
    """Zin Fan Entity."""

    def __init__(self, api: LXZinApi) -> None:
        """Initialize the fan."""
        self.api = api
        self.info: LXZinInfo = api.data
        self.lastChecked: float = 0
        self.SPEED_RANGE = (1, 3)
        self.ORDERED_NAMED_FAN_SPEEDS = ["low", "mid", "high"]

    @property
    def unique_id(self) -> str:
        """Get unique ID."""
        return self.api.deviceId

    @property
    def device_info(self) -> DeviceInfo | None:
        """Get device info."""
        return self.info.deviceInfo if self.info is not None else None

    @property
    def name(self) -> str | None:
        """Return the name of the fan."""
        return self.info.name if self.info is not None else None

    @property
    def translation_key(self) -> str:
        """Get translation key."""
        return "fan"

    @property
    def is_on(self) -> bool:
        """Return true if fan is on."""
        return self.info.power if self.info is not None else False

    @property
    def speed(self) -> int:
        """Return the current speed."""
        return self.info.fanSpeed if self.info is not None else 0

    @property
    def preset_mode(self) -> str | None:
        """Preset modes."""
        if self.info is None or self.info.mode == 0:
            return None
        return Preset(self.info.mode).name

    @property
    def preset_modes(self) -> list[str]:
        """Preset modes."""
        return [e.name for e in Preset]

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode of the fan."""
        _LOGGER.info("Setting preset mode to %s", preset_mode)
        await self.api.preset(Preset[preset_mode])

    @property
    def supported_features(self) -> FanEntityFeature:
        """Return the list of supported features."""
        return FanEntityFeature.SET_SPEED | FanEntityFeature.PRESET_MODE

    @property
    def percentage(self) -> int:
        """Return the current speed percentage."""
        if self.info is None or self.info.fanSpeed == 0:
            return 0
        return ranged_value_to_percentage(self.SPEED_RANGE, self.info.fanSpeed)

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed percentage of the fan."""
        if self.info is None:
            return
        if percentage == 0:
            await self.api.power(False)
            return

        if not self.info.power:
            await self.api.power(True)

        if Preset(self.info.mode) == Preset.FAN:
            speed = math.ceil(percentage_to_ranged_value(self.SPEED_RANGE, percentage))
            await self.api.speed(speed)

    @property
    def speed_count(self) -> int:
        """Return the number of speeds the fan supports."""
        return int_states_in_range(self.SPEED_RANGE)

    async def async_turn_on(
        self,
        speed: Optional[str] = None,
        percentage: Optional[int] = None,
        preset_mode: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Turn on."""
        await self.api.power(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the fan off."""
        await self.api.power(False)

    @property
    def should_poll(self) -> bool:
        """Polling needed for this device."""
        return True

    async def async_update(self) -> None:
        """Fetch new state data for the fan."""
        current = time.time()
        checkTime = 90
        if self.info is not None and not self.info.power:
            checkTime = 180

        if current - self.lastChecked > checkTime:
            await self.api.update()
            self.lastChecked = current

        self.info = self.api.data
