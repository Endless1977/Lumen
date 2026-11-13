"""Odometer and maintenance interval of the car."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfLength
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import LumenCarEntity

# key, data field, name, min, max, step, unit, icon
NUMBERS = (
    ("km_stand", "km", "Lumen auto: huidige km-stand", 0, 2_000_000, 1, UnitOfLength.KILOMETERS, "mdi:counter"),
    ("onderhoud_laatst_km", "service_km", "Lumen auto: km-stand bij laatste onderhoud", 0, 2_000_000, 1, UnitOfLength.KILOMETERS, "mdi:wrench-clock"),
    ("onderhoud_interval_km", "service_interval_km", "Lumen auto: onderhoudsinterval (km)", 1000, 60_000, 500, UnitOfLength.KILOMETERS, "mdi:wrench-cog"),
    ("onderhoud_interval_maanden", "service_interval_months", "Lumen auto: onderhoudsinterval (maanden)", 1, 36, 1, None, "mdi:calendar-sync"),
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, add: AddEntitiesCallback) -> None:
    car = hass.data[DOMAIN]["car"]
    add(LumenCarNumber(car, *n) for n in NUMBERS)


class LumenCarNumber(LumenCarEntity, NumberEntity):
    _attr_mode = NumberMode.BOX

    def __init__(self, car, key, field, name, lo, hi, step, unit, icon) -> None:
        super().__init__(car, key, name, "number")
        self._field = field
        self._attr_native_min_value, self._attr_native_max_value, self._attr_native_step = lo, hi, step
        self._attr_native_unit_of_measurement = unit
        self._attr_icon = icon

    @property
    def native_value(self) -> float | None:
        return self.car.data[self._field]

    async def async_set_native_value(self, value: float) -> None:
        self.car.set(self._field, value)
