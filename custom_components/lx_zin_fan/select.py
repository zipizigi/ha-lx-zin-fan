"""Support for Naver Weather Sensors."""

import logging
from typing import cast

from homeassistant.components.select import SelectEntity
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
    """Set up lamp select."""

    api = cast(LXZinApi, config_entry.runtime_data)
    async_add_entities([ZinLampEntity(api)])


class ZinLampEntity(SelectEntity):
    """Zin Select Entity."""

    def __init__(self, api: LXZinApi) -> None:
        """Initialize the fan."""
        self.api = api
        self.info: LXZinInfo = api.data

    @property
    def unique_id(self) -> str:
        """Get unique ID."""
        return self.api.deviceId

    @property
    def device_info(self) -> DeviceInfo | None:
        """Get device info."""
        return self.info.deviceInfo if self.info is not None else None

    @property
    def current_option(self) -> str | None:
        """Get current lamp option."""
        return self.info.lamp if self.info is not None else None

    @property
    def icon(self) -> str:
        """Get icon."""
        return "mdi:television-ambient-light"

    @property
    def translation_key(self) -> str:
        """Get translation key."""
        return "lamp"

    @property
    def options(self) -> [str]:
        """Get all options."""
        return ["all", "display", "none"]

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        await self.api.lamp(option)

    @property
    def name(self) -> str | None:
        """Return the name of the fan."""
        return self.info.name + " 램프" if self.info is not None else None

    @property
    def should_poll(self) -> bool:
        """Polling needed for this device."""
        return True

    def update(self) -> None:
        """Fetch new state data for the fan."""
        self.info = self.api.data
