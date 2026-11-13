"""Lumen car: data for a car that has no integration of its own.

Licence plate (with an RDW lookup for Dutch cars: make, model, APK date, fuel), odometer,
refuelling log with consumption, maintenance interval and reminders for APK and
maintenance. Everything is kept in Home Assistant's storage; the page shows it on the
Auto tab.
"""

from __future__ import annotations

import calendar
from collections.abc import Callable
from datetime import date, datetime, timedelta
import logging
import re
from typing import Any

import aiohttp

from homeassistant.components import persistent_notification
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_track_time_change
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

_LOGGER = logging.getLogger(__name__)

STORAGE_KEY = "lumen.car"
STORAGE_VERSION = 1
RDW_URL = "https://opendata.rdw.nl/resource/{}.json"
RDW_VEHICLES = "m9d7-ebf2"   # Gekentekende_voertuigen: make, model, APK date
RDW_FUEL = "8ys7-d773"       # Gekentekende_voertuigen_brandstof: fuel, combined consumption

DEFAULTS: dict[str, Any] = {
    "plate": "",
    "rdw": {},
    "km": None,
    "service_date": None,
    "service_km": None,
    "service_interval_km": 15000,
    "service_interval_months": 12,
    "apk_manual": None,
    "refuels": [],
    "fired": [],
}

APK_STEPS = (30, 14, 7, 3, 1, 0)
SERVICE_DAY_STEPS = (30, 14, 7, 3, 1, 0)
SERVICE_KM_STEPS = (500, 0)

TEXTS = {
    "nl": {
        "apk_title": "APK", "apk_due": "De APK van {car} verloopt over {days} dagen.", "apk_over": "De APK van {car} is verlopen!",
        "svc_title": "Onderhoud", "svc_due_km": "Onderhoud voor {car} nodig binnen {km} km.", "svc_due_days": "Onderhoud voor {car} nodig binnen {days} dagen.",
        "svc_now": "Onderhoud voor {car} is nodig.", "car": "de auto",
    },
    "en": {
        "apk_title": "Vehicle inspection (APK)", "apk_due": "The APK of {car} expires in {days} days.", "apk_over": "The APK of {car} has expired!",
        "svc_title": "Maintenance", "svc_due_km": "Maintenance for {car} is due within {km} km.", "svc_due_days": "Maintenance for {car} is due within {days} days.",
        "svc_now": "Maintenance for {car} is due.", "car": "the car",
    },
    "de": {
        "apk_title": "HU (APK)", "apk_due": "Die HU von {car} läuft in {days} Tagen ab.", "apk_over": "Die HU von {car} ist abgelaufen!",
        "svc_title": "Wartung", "svc_due_km": "Wartung für {car} ist fällig innerhalb von {km} km.", "svc_due_days": "Wartung für {car} ist fällig innerhalb von {days} Tagen.",
        "svc_now": "Wartung für {car} ist fällig.", "car": "das Auto",
    },
    "fr": {
        "apk_title": "Contrôle technique", "apk_due": "Le contrôle technique de {car} expire dans {days} jours.", "apk_over": "Le contrôle technique de {car} a expiré !",
        "svc_title": "Entretien", "svc_due_km": "L'entretien de {car} est nécessaire dans {km} km.", "svc_due_days": "L'entretien de {car} est nécessaire dans {days} jours.",
        "svc_now": "L'entretien de {car} est nécessaire.", "car": "la voiture",
    },
}


def clean_plate(value: str) -> str:
    """'ab-123-c' -> 'AB123C'."""
    return re.sub(r"[^A-Za-z0-9]", "", value or "").upper()


def _date(value: Any) -> date | None:
    if not value:
        return None
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def add_months(day: date, months: int) -> date:
    """Same day of the month, months later (the month's last day if it is shorter)."""
    month = day.month - 1 + months
    year, month = day.year + month // 12, month % 12 + 1
    return date(year, month, min(day.day, calendar.monthrange(year, month)[1]))


def refuel_stats(refuels: list[dict[str, Any]]) -> dict[str, Any]:
    """Consumption (l/100 km) from the distance between refuels: the last one and on average."""
    items = sorted(refuels, key=lambda r: r["km"])
    out: dict[str, Any] = {"aantal": len(items), "laatste": None, "gemiddeld": None}
    if len(items) >= 2:
        dist = items[-1]["km"] - items[-2]["km"]
        if dist > 0:
            out["laatste"] = round(items[-1]["liters"] / dist * 100, 2)
        total = items[-1]["km"] - items[0]["km"]
        if total > 0:
            out["gemiddeld"] = round(sum(r["liters"] for r in items[1:]) / total * 100, 2)
    return out


class LumenCar:
    """Keeps the car data, looks up the RDW and sends reminders."""

    def __init__(self, hass: HomeAssistant, notify: str | None = None, lang: str | None = None) -> None:
        self.hass = hass
        self.notify = notify or ""
        self.lang = lang or ""
        self.data: dict[str, Any] = {**DEFAULTS}
        self._store: Store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self._listeners: list[Callable[[], None]] = []
        self._unsubs: list[Callable[[], None]] = []

    # ---- storage and listeners ----
    async def async_load(self) -> None:
        stored = await self._store.async_load()
        if isinstance(stored, dict):
            self.data.update({k: v for k, v in stored.items() if k in DEFAULTS})
        self._unsubs.append(async_track_time_change(self.hass, self._async_daily_rdw, hour=4, minute=10, second=0))
        self._unsubs.append(async_track_time_change(self.hass, self._async_daily_check, hour=9, minute=5, second=0))

    def async_unload(self) -> None:
        for unsub in self._unsubs:
            unsub()
        self._unsubs.clear()

    @callback
    def add_listener(self, listener: Callable[[], None]) -> Callable[[], None]:
        self._listeners.append(listener)
        return lambda: self._listeners.remove(listener)

    @callback
    def _changed(self, check: bool = True) -> None:
        self._store.async_delay_save(lambda: self.data, 1)
        for listener in list(self._listeners):
            listener()
        if check:
            self.check_reminders()

    @callback
    def set(self, key: str, value: Any) -> None:
        if key in ("service_date", "apk_manual") and value is not None:
            value = _date(value).isoformat() if _date(value) else None
        self.data[key] = value
        self._changed()

    # ---- licence plate and RDW ----
    async def async_set_plate(self, plate: str) -> None:
        plate = clean_plate(plate)
        if plate == self.data["plate"] and self.data["rdw"]:
            return
        self.data["plate"] = plate
        self.data["rdw"] = {}
        self._changed(check=False)
        if plate:
            await self.async_rdw()

    async def async_rdw(self) -> dict[str, Any]:
        """Look the plate up in the RDW open data (Dutch plates, no key needed)."""
        plate = self.data["plate"]
        if not plate:
            return {}
        out: dict[str, Any] = {"kenteken": plate, "fout": None}
        session = async_get_clientsession(self.hass)
        timeout = aiohttp.ClientTimeout(total=10)
        try:
            async with session.get(RDW_URL.format(RDW_VEHICLES), params={"kenteken": plate}, timeout=timeout) as resp:
                resp.raise_for_status()
                rows = await resp.json(content_type=None)
            if not rows:
                out["fout"] = "kenteken niet gevonden bij RDW"
            else:
                v = rows[0]
                out.update(
                    merk=v.get("merk"), model=v.get("handelsbenaming"), voertuigsoort=v.get("voertuigsoort"),
                    apk_datum=(v.get("vervaldatum_apk_dt") or "")[:10] or None,
                    eerste_toelating=(v.get("datum_eerste_toelating_dt") or "")[:10] or None,
                )
                try:
                    async with session.get(RDW_URL.format(RDW_FUEL), params={"kenteken": plate}, timeout=timeout) as resp:
                        resp.raise_for_status()
                        fuel = await resp.json(content_type=None)
                    if fuel:
                        out["brandstof"] = fuel[0].get("brandstof_omschrijving")
                        use = fuel[0].get("brandstofverbruik_gecombineerd")
                        out["verbruik_fabriek"] = float(use) if use else None
                except (aiohttp.ClientError, TimeoutError, ValueError):
                    pass   # fuel data is a bonus
        except (aiohttp.ClientError, TimeoutError, ValueError) as err:
            out["fout"] = f"RDW-opzoeking mislukt: {err}"
            # keep what we knew before a temporary failure
            if self.data["rdw"].get("merk"):
                out = {**self.data["rdw"], "fout": out["fout"]}
        if plate == self.data["plate"]:
            self.data["rdw"] = out
            self._changed()
        return out

    async def _async_daily_rdw(self, _now: datetime) -> None:
        if self.data["plate"]:
            await self.async_rdw()

    # ---- refuelling ----
    @callback
    def add_refuel(self, day: date, km: float, liters: float, price: float | None = None) -> None:
        if km <= 0 or liters <= 0:
            raise ValueError("km en liters moeten groter dan 0 zijn")
        if any(r["km"] >= km for r in self.data["refuels"]):
            raise ValueError(f"km-stand {km:g} is niet hoger dan een eerdere tankbeurt")
        self.data["refuels"] = [*self.data["refuels"], {"datum": day.isoformat(), "km": km, "liters": liters, "prijs": price}]
        if not self.data["km"] or km > self.data["km"]:
            self.data["km"] = km
        self._changed()

    @callback
    def remove_last_refuel(self) -> None:
        if self.data["refuels"]:
            items = sorted(self.data["refuels"], key=lambda r: r["km"])
            self.data["refuels"] = items[:-1]
            self._changed()

    # ---- what the page and the reminders use ----
    def apk_date(self) -> date | None:
        return _date(self.data["rdw"].get("apk_datum")) or _date(self.data["apk_manual"])

    def service_next(self) -> tuple[float | None, date | None]:
        d = self.data
        km = (d["service_km"] or 0) + (d["service_interval_km"] or 15000) if d["service_km"] is not None else None
        day = add_months(_date(d["service_date"]), int(d["service_interval_months"] or 12)) if _date(d["service_date"]) else None
        return km, day

    def attributes(self) -> dict[str, Any]:
        d, rdw = self.data, self.data["rdw"]
        today = dt_util.now().date()
        apk = self.apk_date()
        next_km, next_day = self.service_next()
        stats = refuel_stats(d["refuels"])
        return {
            "lumen_integratie": True,
            "merk": rdw.get("merk"), "model": rdw.get("model"), "voertuigsoort": rdw.get("voertuigsoort"),
            "brandstof": rdw.get("brandstof"), "verbruik_fabriek": rdw.get("verbruik_fabriek"),
            "eerste_toelating": rdw.get("eerste_toelating"), "rdw_fout": rdw.get("fout"),
            "apk_datum": apk.isoformat() if apk else None,
            "apk_dagen": (apk - today).days if apk else None,
            "km_stand": d["km"],
            "onderhoud_laatst": d["service_date"], "onderhoud_laatst_km": d["service_km"],
            "onderhoud_volgende_km": next_km,
            "onderhoud_km_resterend": round(next_km - (d["km"] or 0)) if next_km is not None and d["km"] is not None else None,
            "onderhoud_volgende_datum": next_day.isoformat() if next_day else None,
            "onderhoud_dagen_resterend": (next_day - today).days if next_day else None,
            "verbruik_laatste": stats["laatste"], "verbruik_gemiddeld": stats["gemiddeld"],
            "tankbeurten": sorted(d["refuels"], key=lambda r: r["km"])[-10:],
        }

    # ---- reminders ----
    def _lang(self) -> str:
        st = self.hass.states.get("input_select.lumen_taal")
        lang = (st.state if st and st.state in TEXTS else self.lang or self.hass.config.language or "nl").split("-")[0].lower()
        return lang if lang in TEXTS else "en"

    def _car_name(self, t: dict[str, str]) -> str:
        rdw = self.data["rdw"]
        name = " ".join(x for x in (rdw.get("merk"), rdw.get("model")) if x)
        return (name.title() if name.isupper() else name) or self.data["plate"] or t["car"]

    @callback
    def check_reminders(self) -> None:
        """Send each reminder once per threshold (30, 14, 7, 3, 1, 0 days; 500 and 0 km)."""
        attrs = self.attributes()
        fired: set[str] = set(self.data["fired"])
        new = set(fired)
        t = TEXTS[self._lang()]
        car = self._car_name(t)
        msgs: list[tuple[str, str, str]] = []

        def due(prefix: str, value: float | None, steps: tuple[int, ...], key: str) -> bool:
            if value is None:
                return False
            hit = [s for s in steps if value <= s]
            keys = {f"{prefix}:{key}:{s}" for s in hit}
            if keys - fired:
                new.update(keys)
                return True
            return False

        apk_days, apk = attrs["apk_dagen"], attrs["apk_datum"]
        if due("apk", apk_days, APK_STEPS, str(apk)):
            msgs.append(("lumen_auto_apk", t["apk_title"], (t["apk_over"] if apk_days < 0 else t["apk_due"]).format(car=car, days=apk_days)))
        svc_key = f"{self.data['service_date']}|{self.data['service_km']}"
        km_left, days_left = attrs["onderhoud_km_resterend"], attrs["onderhoud_dagen_resterend"]
        km_hit = due("svc_km", km_left, SERVICE_KM_STEPS, svc_key)
        day_hit = due("svc_day", days_left, SERVICE_DAY_STEPS, svc_key)
        if km_hit or day_hit:
            if (km_left is not None and km_left <= 0) or (days_left is not None and days_left <= 0):
                text = t["svc_now"].format(car=car)
            elif km_hit:
                text = t["svc_due_km"].format(car=car, km=round(km_left))
            else:
                text = t["svc_due_days"].format(car=car, days=days_left)
            msgs.append(("lumen_auto_onderhoud", t["svc_title"], text))

        if new != fired:
            # forget thresholds of older APK dates / service intervals
            keep_apk, keep_svc = f"apk:{apk}:", f":{svc_key}:"
            self.data["fired"] = sorted(k for k in new if k.startswith(keep_apk) or keep_svc in k)
            self._store.async_delay_save(lambda: self.data, 1)
        for notif_id, title, text in msgs:
            self._send(notif_id, title, text)

    def _send(self, notif_id: str, title: str, text: str) -> None:
        persistent_notification.async_create(self.hass, text, title=f"Lumen: {title}", notification_id=notif_id)
        if self.hass.states.get("input_text.lumen_melding"):
            stamp = dt_util.now().strftime("%H:%M:%S")
            self.hass.async_create_task(self.hass.services.async_call(
                "input_text", "set_value", {"entity_id": "input_text.lumen_melding", "value": f"{stamp}|{text}"[:255]}))
        if self.notify:
            domain, _, service = self.notify.partition(".")
            if domain == "notify" and service and self.hass.services.has_service("notify", service):
                self.hass.async_create_task(self.hass.services.async_call("notify", service, {"title": f"Lumen: {title}", "message": text}))
        self.hass.bus.async_fire("lumen_auto_herinnering", {"title": title, "message": text, "type": notif_id})

    async def _async_daily_check(self, _now: datetime) -> None:
        for listener in list(self._listeners):
            listener()
        self.check_reminders()
