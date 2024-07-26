"""Config flow for LX Z:in Fan integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .zin_api import LXZinApi

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("userId"): str,
        vol.Required("deviceId"): str,
    }
)


async def getDeviceName(hass: HomeAssistant, userId: str, deviceId: str) -> str:
    """Get device name."""
    api = LXZinApi(userId, deviceId)
    await api.update()
    return api.data.name


class ConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for LX Z:in Fan."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            await self.async_set_unique_id(user_input["deviceId"])
            self._abort_if_unique_id_configured()
            deviceName = await getDeviceName(
                self.hass, user_input["userId"], user_input["deviceId"]
            )

            return self.async_create_entry(title=deviceName, data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )
