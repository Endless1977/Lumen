"""Lumen's own car data: licence plate with RDW lookup, refuelling, maintenance, reminders."""

from datetime import timedelta

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from homeassistant.util import dt as dt_util

from custom_components.lumen.car import add_months, clean_plate, refuel_stats
from custom_components.lumen.const import DOMAIN

RDW = "https://opendata.rdw.nl/resource/{}.json"


async def _setup(hass: HomeAssistant):
    assert await async_setup_component(hass, "http", {})
    assert await async_setup_component(hass, "frontend", {})
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {"title": "Lumen", "lang": "nl"})
    await hass.async_block_till_done()
    return hass.config_entries.async_entries(DOMAIN)[0]


def test_helpers() -> None:
    assert clean_plate("ab-123 c") == "AB123C"
    assert add_months(dt_util.parse_date("2026-01-31"), 1).isoformat() == "2026-02-28"
    assert add_months(dt_util.parse_date("2026-11-15"), 12).isoformat() == "2027-11-15"
    s = refuel_stats([{"km": 1000, "liters": 40}, {"km": 1500, "liters": 30}, {"km": 2100, "liters": 33}])
    assert s["laatste"] == 5.5 and s["gemiddeld"] == round(63 / 1100 * 100, 2)


async def test_car_entities_rdw_refuel_and_reminders(hass: HomeAssistant, aioclient_mock) -> None:
    aioclient_mock.get(RDW.format("m9d7-ebf2"), json=[{"merk": "HYUNDAI", "handelsbenaming": "I10", "voertuigsoort": "Personenauto",
                                                       "vervaldatum_apk_dt": (dt_util.now().date() + timedelta(days=5)).isoformat() + "T00:00:00.000"}])
    aioclient_mock.get(RDW.format("8ys7-d773"), json=[{"brandstof_omschrijving": "Benzine", "brandstofverbruik_gecombineerd": "5.00"}])
    entry = await _setup(hass)
    for eid in ("sensor.lumen_auto", "text.lumen_auto_kenteken", "number.lumen_auto_km_stand", "number.lumen_auto_onderhoud_interval_km",
                "date.lumen_auto_onderhoud_laatst", "date.lumen_auto_apk_handmatig"):
        assert hass.states.get(eid) is not None, eid
    assert hass.states.get("sensor.lumen_auto").attributes["lumen_integratie"] is True

    events = []
    hass.bus.async_listen("lumen_auto_herinnering", lambda e: events.append(e.data))

    await hass.services.async_call("text", "set_value", {"entity_id": "text.lumen_auto_kenteken", "value": "ab-123-c"}, blocking=True)
    await hass.async_block_till_done()
    st = hass.states.get("sensor.lumen_auto")
    assert st.state == "AB123C"
    assert st.attributes["merk"] == "HYUNDAI" and st.attributes["brandstof"] == "Benzine" and st.attributes["verbruik_fabriek"] == 5.0
    assert st.attributes["apk_dagen"] == 5
    # APK in 5 days: one reminder, not repeated
    assert len([e for e in events if e["type"] == "lumen_auto_apk"]) == 1
    assert "over 5 dagen" in events[0]["message"]
    hass.data[DOMAIN]["car"].check_reminders()
    await hass.async_block_till_done()
    assert len([e for e in events if e["type"] == "lumen_auto_apk"]) == 1

    # refuelling updates the odometer and the consumption
    await hass.services.async_call(DOMAIN, "auto_tankbeurt", {"datum": "2026-10-01", "km": 1000, "liters": 40}, blocking=True)
    await hass.services.async_call(DOMAIN, "auto_tankbeurt", {"km": 1500, "liters": 30, "prijs": 55.5}, blocking=True)
    await hass.async_block_till_done()
    st = hass.states.get("sensor.lumen_auto")
    assert hass.states.get("number.lumen_auto_km_stand").state == "1500.0"
    assert st.attributes["verbruik_laatste"] == 6.0 and len(st.attributes["tankbeurten"]) == 2
    # a lower odometer reading is refused
    try:
        await hass.services.async_call(DOMAIN, "auto_tankbeurt", {"km": 1200, "liters": 10}, blocking=True)
        raise AssertionError("expected an error")
    except Exception as err:  # noqa: BLE001
        assert "niet hoger" in str(err)
    await hass.services.async_call(DOMAIN, "auto_tankbeurt_verwijderen", {}, blocking=True)
    await hass.async_block_till_done()
    assert len(hass.states.get("sensor.lumen_auto").attributes["tankbeurten"]) == 1

    # maintenance: last service 14,800 km ago with a 15,000 km interval -> one reminder
    await hass.services.async_call("number", "set_value", {"entity_id": "number.lumen_auto_km_stand", "value": 20000}, blocking=True)
    await hass.services.async_call("number", "set_value", {"entity_id": "number.lumen_auto_onderhoud_laatst_km", "value": 5200}, blocking=True)
    await hass.async_block_till_done()
    st = hass.states.get("sensor.lumen_auto")
    assert st.attributes["onderhoud_km_resterend"] == 200
    assert len([e for e in events if e["type"] == "lumen_auto_onderhoud"]) == 1

    # stored, and the entities go away on unload
    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    assert not hass.services.has_service(DOMAIN, "auto_tankbeurt")
