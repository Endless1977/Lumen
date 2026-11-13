"""Shared base for Lumen's car entities."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity import Entity

from .car import LumenCar
from .const import DOMAIN


class LumenCarEntity(Entity):
    """An entity of the car without an integration of its own; follows LumenCar."""

    _attr_should_poll = False
    _attr_has_entity_name = False

    def __init__(self, car: LumenCar, key: str, name: str, domain: str) -> None:
        self.car = car
        self._attr_unique_id = f"{DOMAIN}_auto_{key}"
        self._attr_name = name
        # fixed entity ids, so the page finds them (a free id is chosen if one is taken)
        self.entity_id = f"{domain}.lumen_auto" + (f"_{key}" if key else "")
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, "auto")}, name="Lumen auto", manufacturer="Lumen",
            model="Auto zonder eigen integratie", entry_type=DeviceEntryType.SERVICE,
        )

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(self.car.add_listener(self.async_write_ha_state))
