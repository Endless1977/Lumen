"""Date of the last maintenance, and the APK date when the RDW does not know it."""

from __future__ import annotations

from datetime import date

from homeassistant.components.date import DateEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .car import _date
from .const import DOMAIN
from .entity import LumenCarEntity

DATES = (
    ("onderhoud_laatst", "service_date", "Lumen auto: datum laatste onderhoud", "mdi:wrench-clock"),
    ("apk_handmatig", "apk_manual", "Lumen auto: volgende APK (alleen als de RDW niets geeft)", "mdi:calendar-check"),
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, add: AddEntitiesCallback) -> None:
    car = hass.data[DOMAIN]["car"]
    add(LumenCarDate(car, *d) for d in DATES)


class LumenCarDate(LumenCarEntity, DateEntity):
    def __init__(self, car, key, field, name, icon) -> None:
        super().__init__(car, key, name, "date")
        self._field = field
        self._attr_icon = icon

    @property
    def native_value(self) -> date | None:
        return _date(self.car.data[self._field])

    async def async_set_value(self, value: date) -> None:
        self.car.set(self._field, value.isoformat())
