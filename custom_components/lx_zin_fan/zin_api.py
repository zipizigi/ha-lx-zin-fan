"""LX Z:in API."""

import asyncio
import logging

import aiohttp
import dateutil.parser
import jwt

from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN, Preset

_LOGGER = logging.getLogger(__name__)


class LXZinInfo:
    """LX Zin Api Info."""

    def __init__(self, json) -> None:
        """Init."""
        sensor = json["sensor"]
        device = json["device"]
        self.userId = str(json["ownerId"])
        self.deviceId = str(json["_id"])
        self.name = str(device["name"])
        self.co2 = int(sensor["airCondition"]["co2"])
        self.pm25 = int(sensor["airCondition"]["pm2_5"])
        self.tvoc = int(sensor["airCondition"]["tvocs"])
        self.temperature = int(sensor["airCondition"]["temperature"])
        self.humidity = int(sensor["airCondition"]["humidity"])

        self.fanSpeed = int(sensor["fan"]["fanSpeed"])
        self.mode = int(sensor["mode"])

        self.lamp = str(sensor["lamp"]["style"])
        self.power = str(sensor["power"]["status"]) == "on"

        heatExchangerLifeTime = int(sensor["heatExchanger"]["lifeTime"])
        heatExchangerUsageTime = int(sensor["heatExchanger"]["usageTime"])
        self.heatExchanger = int(
            (heatExchangerLifeTime - heatExchangerUsageTime)
            / heatExchangerLifeTime
            * 100
        )
        filterLifeTime = int(sensor["filter"]["filterLifeTime"])
        filterUsageTime = int(sensor["filter"]["filterUsageTime"])
        self.filter = int((filterLifeTime - filterUsageTime) / filterLifeTime * 100)
        self.lastUpdated = dateutil.parser.parse(str(json["lastUpdatedAt"]))

        self.deviceInfo = DeviceInfo(
            manufacturer=str(device["manufacturer"]),
            serial_number=str(device["serialNo"]),
            name=str(device["name"]),
            model=str(device["type"]),
            sw_version=str(device["firmware"]["modem"]["version"]),
            hw_version=str(device["firmware"]["mcu"]["version"]),
            identifiers={(DOMAIN, self.deviceId)},
        )

    def __getitem__(self, key):
        """Get with []."""
        return self.__dict__[key]

    def __str__(self) -> str:
        """Info to str."""
        return f"name: {self.name}, power: {self.power}, fanSpeed: {self.fanSpeed}, mode: {self.mode}, temp: {self.temperature}, humi: {self.humidity}"


class LXZinApi:
    """Zin api."""

    def __init__(self, userId: str, deviceId: str) -> None:
        """Init."""
        self.userId = userId
        self.deviceId = deviceId
        self.data: LXZinInfo = None

    async def update(self):
        """Update status."""
        try:
            url = (
                "https://iot-service.lxhausys.com/service/api/v1/device/"
                + self.deviceId
            )
            token = jwt.encode({"userId": self.userId}, "secret", algorithm="HS256")
            header = {"Authorization": ("Bearer " + token)}
            async with (
                aiohttp.ClientSession() as session,
                session.get(url, headers=header, timeout=30) as response,
            ):
                response.raise_for_status()

                apiResponse = await response.json()
                self.data = LXZinInfo(apiResponse)
                _LOGGER.info("Zin info api <-- %s", self.data)

        except Exception as ex:
            _LOGGER.error("Failed to update LX Z:in API status Error: %s", ex)
            raise

    async def power(self, isOn: bool):
        """On/Off Power."""
        body = ""
        if isOn:
            body = '{"sensor":{"power":{"status":"on"}}}'
        else:
            body = '{"sensor":{"power":{"status":"off"}}}'
        await self.desired(body)

    async def preset(self, preset: Preset):
        """Set preset."""
        body = '{"sensor":{"mode":"' + str(preset.value) + '"}}'
        await self.desired(body)

    async def speed(self, speed: int):
        """Set preset."""
        body = '{"sensor":{"fan":{"fanSpeed":"' + str(speed) + '"}}}'
        await self.desired(body)

    async def lamp(self, style: str):
        """Set lamp."""
        body = '{"sensor":{"lamp":{"style":"' + style + '"}}}'
        await self.desired(body)

    async def desired(self, body: str):
        """Update fan."""
        try:
            url = (
                "https://iot-service.lxhausys.com/service/api/v1/device/"
                + self.deviceId
                + "/desired"
            )
            token = jwt.encode({"userId": self.userId}, "secret", algorithm="HS256")
            header = {
                "Authorization": ("Bearer " + token),
                "Content-Type": "application/json",
            }
            _LOGGER.info("Zin api --> %s", body)

            async with (
                aiohttp.ClientSession() as session,
                session.post(url, headers=header, data=body, timeout=30) as response,
            ):
                response.raise_for_status()

                apiResponse = await response.text()
                _LOGGER.info("Zin api <-- %s", apiResponse)
                await asyncio.sleep(0.5)
                await self.update()

        except Exception as ex:
            _LOGGER.error("Failed to update LX Z:in API Error: %s", ex)
            raise
