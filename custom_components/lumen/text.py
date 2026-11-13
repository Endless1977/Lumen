"""Licence plate of the car (setting it looks the car up at the RDW)."""

from __future__ import annotations

from homeassistant.components.text import TextEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import LumenCarEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, add: AddEntitiesCallback) -> None:
    add([LumenPlate(hass.data[DOMAIN]["car"], "kenteken", "Lumen auto: kenteken", "text")])


class LumenPlate(LumenCarEntity, TextEntity):
    _attr_icon = "mdi:card-text-outline"
    _attr_native_max = 12
    _attr_pattern = r"^[A-Za-z0-9 \-]*$"

    @property
    def native_value(self) -> str:
        return self.car.data["plate"]

    async def async_set_value(self, value: str) -> None:
        await self.car.async_set_plate(value)
