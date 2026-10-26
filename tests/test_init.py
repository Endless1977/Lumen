"""Lumen sets up a sidebar panel and serves its page."""

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component

from custom_components.lumen.const import DOMAIN, PANEL_URL_PATH


async def _setup(hass: HomeAssistant, data: dict):
    assert await async_setup_component(hass, "http", {})
    assert await async_setup_component(hass, "frontend", {})
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    assert result["type"] == "form"
    result = await hass.config_entries.flow.async_configure(result["flow_id"], data)
    assert result["type"] == "create_entry"
    await hass.async_block_till_done()
    return hass.config_entries.async_entries(DOMAIN)[0]


async def test_panel_and_options(hass: HomeAssistant, hass_client) -> None:
    entry = await _setup(hass, {"title": "Lumen", "lang": "nl", "place": "Utrecht"})
    panels = hass.data["frontend_panels"]
    assert PANEL_URL_PATH in panels
    url = panels[PANEL_URL_PATH].config["url"]
    assert url.startswith("/lumen_static/lumen.html?") and "place=Utrecht" in url

    client = await hass_client()
    resp = await client.get("/lumen_static/lumen.html")
    assert resp.status == 200
    assert "LUMEN_VERSION" in await resp.text()
    resp = await client.get("/lumen_static/girl_bust.glb")
    assert resp.status == 200

    # second setup is refused
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    assert result["type"] == "abort"

    # options change the panel
    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] == "form"
    result = await hass.config_entries.options.async_configure(result["flow_id"], {"title": "Hologram", "lang": "en"})
    assert result["type"] == "create_entry"
    await hass.async_block_till_done()
    panel = hass.data["frontend_panels"][PANEL_URL_PATH]
    assert panel.sidebar_title == "Hologram" and "lang=en" in panel.config["url"]

    # unloading removes the panel
    assert await hass.config_entries.async_unload(entry.entry_id)
    assert PANEL_URL_PATH not in hass.data["frontend_panels"]
