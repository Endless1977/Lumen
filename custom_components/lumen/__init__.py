"""Lumen: a holographic talking assistant for Home Assistant.

The integration serves the Lumen page and its bundled 3D models, adds Lumen to the
sidebar, and keeps the data of a car that has no integration of its own (licence plate
with RDW lookup, refuelling, maintenance and APK reminders). Lumen itself runs in the browser and talks to Home Assistant over the normal
REST and WebSocket APIs with the logged-in user's session.
"""

from __future__ import annotations

from pathlib import Path
from urllib.parse import urlencode

import voluptuous as vol

from homeassistant.components import frontend
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv
from homeassistant.util import dt as dt_util

from .car import LumenCar

from .const import (
    CONF_ADMIN_ONLY,
    CONF_ICON,
    CONF_LANG,
    CONF_NOTIFY,
    CONF_TITLE,
    DEFAULT_ICON,
    DEFAULT_TITLE,
    DOMAIN,
    PAGE_OPTIONS,
    PANEL_URL_PATH,
    PLATFORMS,
    URL_BASE,
    VERSION,
)

WWW = Path(__file__).parent / "www"


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Serve the page and register the sidebar panel."""
    data = hass.data.setdefault(DOMAIN, {})
    if not data.get("static"):
        # Static paths cannot be unregistered, so register them once per run.
        # No long cache headers: Lumen checks its own version and reloads itself.
        await hass.http.async_register_static_paths(
            [StaticPathConfig(URL_BASE, str(WWW), cache_headers=False)]
        )
        data["static"] = True

    opts = {**entry.data, **entry.options}
    query = {"v": VERSION}
    for key in PAGE_OPTIONS:
        value = opts.get(key)
        if value:
            query[key] = value

    frontend.async_register_built_in_panel(
        hass,
        component_name="iframe",
        sidebar_title=opts.get(CONF_TITLE) or DEFAULT_TITLE,
        sidebar_icon=opts.get(CONF_ICON) or DEFAULT_ICON,
        frontend_url_path=PANEL_URL_PATH,
        config={"url": f"{URL_BASE}/lumen.html?{urlencode(query)}"},
        require_admin=bool(opts.get(CONF_ADMIN_ONLY, False)),
        update=True,
    )

    car = LumenCar(hass, opts.get(CONF_NOTIFY), opts.get(CONF_LANG))
    await car.async_load()
    data["car"] = car
    _register_services(hass)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    car.check_reminders()

    entry.async_on_unload(entry.add_update_listener(_async_reload))
    return True


REFUEL_SCHEMA = vol.Schema(
    {
        vol.Optional("datum"): cv.date,
        vol.Required("km"): vol.All(vol.Coerce(float), vol.Range(min=0.1)),
        vol.Required("liters"): vol.All(vol.Coerce(float), vol.Range(min=0.1)),
        vol.Optional("prijs"): vol.Any(None, vol.All(vol.Coerce(float), vol.Range(min=0))),
    }
)


def _register_services(hass: HomeAssistant) -> None:
    """lumen.auto_tankbeurt, lumen.auto_tankbeurt_verwijderen and lumen.auto_rdw_ophalen."""
    if hass.services.has_service(DOMAIN, "auto_tankbeurt"):
        return

    def car() -> LumenCar:
        c = hass.data.get(DOMAIN, {}).get("car")
        if c is None:
            raise HomeAssistantError("Lumen is not set up")
        return c

    async def refuel(call: ServiceCall) -> None:
        try:
            car().add_refuel(call.data.get("datum") or dt_util.now().date(), call.data["km"], call.data["liters"], call.data.get("prijs"))
        except ValueError as err:
            raise HomeAssistantError(str(err)) from err

    async def remove_last(call: ServiceCall) -> None:
        car().remove_last_refuel()

    async def rdw(call: ServiceCall) -> None:
        await car().async_rdw()

    hass.services.async_register(DOMAIN, "auto_tankbeurt", refuel, schema=REFUEL_SCHEMA)
    hass.services.async_register(DOMAIN, "auto_tankbeurt_verwijderen", remove_last)
    hass.services.async_register(DOMAIN, "auto_rdw_ophalen", rdw)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Remove the sidebar panel and the car entities."""
    frontend.async_remove_panel(hass, PANEL_URL_PATH)
    ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    data = hass.data.get(DOMAIN, {})
    car = data.pop("car", None)
    if car:
        car.async_unload()
    for service in ("auto_tankbeurt", "auto_tankbeurt_verwijderen", "auto_rdw_ophalen"):
        hass.services.async_remove(DOMAIN, service)
    return ok


async def _async_reload(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Apply changed options."""
    await hass.config_entries.async_reload(entry.entry_id)
