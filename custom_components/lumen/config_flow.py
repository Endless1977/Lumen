"""Config flow for Lumen."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    CONF_ADMIN_ONLY,
    CONF_AGENT,
    CONF_ICON,
    CONF_LANG,
    CONF_PLACE,
    CONF_STT,
    CONF_TITLE,
    CONF_TTS,
    CONF_VOICE,
    DEFAULT_ICON,
    DEFAULT_TITLE,
    DOMAIN,
)


def _schema(defaults: dict[str, Any], lang: str) -> vol.Schema:
    """Form shared by setup and options."""

    def d(key: str, fallback: Any = "") -> dict[str, Any]:
        value = defaults.get(key, fallback)
        return {"default": value} if value not in (None, "") else {}

    return vol.Schema(
        {
            vol.Optional(CONF_TITLE, **d(CONF_TITLE, DEFAULT_TITLE)): str,
            vol.Optional(CONF_ICON, **d(CONF_ICON, DEFAULT_ICON)): selector.IconSelector(),
            vol.Optional(CONF_ADMIN_ONLY, default=defaults.get(CONF_ADMIN_ONLY, False)): bool,
            vol.Optional(CONF_AGENT, **d(CONF_AGENT)): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="conversation")
            ),
            vol.Optional(CONF_TTS, **d(CONF_TTS)): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="tts")
            ),
            vol.Optional(CONF_VOICE, **d(CONF_VOICE)): str,
            vol.Optional(CONF_STT, **d(CONF_STT)): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="stt")
            ),
            vol.Optional(CONF_LANG, **d(CONF_LANG, lang)): str,
            vol.Optional(CONF_PLACE, **d(CONF_PLACE)): str,
        }
    )


class LumenConfigFlow(ConfigFlow, domain=DOMAIN):
    """Set up Lumen (one per Home Assistant)."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()
        if user_input is not None:
            return self.async_create_entry(title=user_input.get(CONF_TITLE) or DEFAULT_TITLE, data=user_input)
        lang = (self.hass.config.language or "nl").split("-")[0]
        return self.async_show_form(step_id="user", data_schema=_schema({}, lang))

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return LumenOptionsFlow()


class LumenOptionsFlow(OptionsFlow):
    """Change Lumen's sidebar entry and the defaults handed to the page."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(data=user_input)
        current = {**self.config_entry.data, **self.config_entry.options}
        lang = (self.hass.config.language or "nl").split("-")[0]
        return self.async_show_form(step_id="init", data_schema=_schema(current, lang))
