"""The blueprints write the values Lumen expects."""

import shutil
from datetime import timedelta
from pathlib import Path

import yaml
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import async_fire_time_changed

ROOT = Path(__file__).parent.parent


async def _setup(hass: HomeAssistant, automations: list) -> None:
    dst = Path(hass.config.path("blueprints/automation/lumen"))
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(ROOT / "blueprints/automation/lumen", dst, dirs_exist_ok=True)
    pkg = yaml.safe_load((ROOT / "packages/lumen.yaml").read_text())
    for domain in ("input_text", "input_select"):
        assert await async_setup_component(hass, domain, {domain: pkg[domain]})
    assert await async_setup_component(hass, "input_boolean", {"input_boolean": {"knop": {}}})
    assert await async_setup_component(hass, "automation", {"automation": automations})
    await hass.async_block_till_done()


async def test_deurbel_dier_melding(hass: HomeAssistant) -> None:
    await _setup(hass, [
        {"use_blueprint": {"path": "lumen/deurbel.yaml", "input": {"bel": "input_boolean.knop", "camera": "camera.voordeur"}}},
        {"use_blueprint": {"path": "lumen/melding.yaml", "input": {"entiteit": "input_boolean.knop", "naar": "off", "tekst": "Klaar: {{ 2 + 3 }}"}}},
    ])
    await hass.services.async_call("input_boolean", "turn_on", {"entity_id": "input_boolean.knop"}, blocking=True)
    await hass.async_block_till_done()
    parts = hass.states.get("input_text.lumen_deurbel").state.split("|")
    assert parts[1:] == ["camera.voordeur", "bel", ""]
    await hass.services.async_call("input_boolean", "turn_off", {"entity_id": "input_boolean.knop"}, blocking=True)
    await hass.async_block_till_done()
    assert hass.states.get("input_text.lumen_melding").state.endswith("|Klaar: 5")


async def test_dier(hass: HomeAssistant) -> None:
    await _setup(hass, [
        {"use_blueprint": {"path": "lumen/dier.yaml", "input": {"dier": "input_boolean.knop", "camera": "camera.achterdeur", "tekst": "De kat staat bij de achterdeur"}}},
    ])
    await hass.services.async_call("input_boolean", "turn_on", {"entity_id": "input_boolean.knop"}, blocking=True)
    await hass.async_block_till_done()
    first = hass.states.get("input_text.lumen_deurbel").state
    assert first.split("|")[1:] == ["camera.achterdeur", "dier", "De kat staat bij de achterdeur"]
    # again within 3 minutes: no new event
    for svc in ("turn_off", "turn_on"):
        await hass.services.async_call("input_boolean", svc, {"entity_id": "input_boolean.knop"}, blocking=True)
    await hass.async_block_till_done()
    assert hass.states.get("input_text.lumen_deurbel").state == first


async def test_waarschuwing_terug(hass: HomeAssistant, freezer) -> None:
    await _setup(hass, [{"use_blueprint": {"path": "lumen/waarschuwing_terug.yaml", "input": {"minuten": 10}}}])
    await hass.services.async_call("input_select", "select_option", {"entity_id": "input_select.lumen_modus", "option": "waarschuwing"}, blocking=True)
    await hass.async_block_till_done()
    freezer.tick(timedelta(minutes=11))
    async_fire_time_changed(hass, fire_all=True)
    await hass.async_block_till_done()
    assert hass.states.get("input_select.lumen_modus").state == "normaal"
    # an alarm stays
    await hass.services.async_call("input_select", "select_option", {"entity_id": "input_select.lumen_modus", "option": "alarm"}, blocking=True)
    await hass.async_block_till_done()
    freezer.tick(timedelta(minutes=30))
    async_fire_time_changed(hass, fire_all=True)
    await hass.async_block_till_done()
    assert hass.states.get("input_select.lumen_modus").state == "alarm"
