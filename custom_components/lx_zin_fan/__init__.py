"""The LX Z:in Fan integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .zin_api import LXZinApi

PLATFORMS: list[Platform] = [
    Platform.FAN,
    Platform.SELECT,
    Platform.SENSOR,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry[LXZinApi]) -> bool:
    """Set up LX Z:in Fan from a config entry."""

    entry.runtime_data = LXZinApi(entry.data.get("userId"), entry.data.get("deviceId"))
    await entry.runtime_data.update()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry[LXZinApi]) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
