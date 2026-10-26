"""Lumen: a holographic talking assistant for Home Assistant.

The integration serves the Lumen page and its bundled 3D model, and adds Lumen to the
sidebar. Lumen itself runs in the browser and talks to Home Assistant over the normal
REST and WebSocket APIs with the logged-in user's session.
"""

from __future__ import annotations

from pathlib import Path
from urllib.parse import urlencode

from homeassistant.components import frontend
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (
    CONF_ADMIN_ONLY,
    CONF_ICON,
    CONF_TITLE,
    DEFAULT_ICON,
    DEFAULT_TITLE,
    DOMAIN,
    PAGE_OPTIONS,
    PANEL_URL_PATH,
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

    entry.async_on_unload(entry.add_update_listener(_async_reload))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Remove the sidebar panel."""
    frontend.async_remove_panel(hass, PANEL_URL_PATH)
    return True


async def _async_reload(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Apply changed options."""
    await hass.config_entries.async_reload(entry.entry_id)
