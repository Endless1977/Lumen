"""Sensor with everything Lumen knows about the car (state: licence plate)."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import LumenCarEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, add: AddEntitiesCallback) -> None:
    add([LumenCarSensor(hass.data[DOMAIN]["car"], "", "Lumen auto", "sensor")])


class LumenCarSensor(LumenCarEntity, SensorEntity):
    _attr_icon = "mdi:car-info"

    @property
    def native_value(self) -> str | None:
        return self.car.data["plate"] or None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return self.car.attributes()
