# Entities Lumen uses

Everything is optional. Lumen shows a feature only when its entities exist. Helpers marked
**(package)** are created by [`packages/lumen.yaml`](../packages/lumen.yaml); the others you make
yourself, usually as template sensors on top of your own devices.

Timestamps in text helpers are ISO (`{{ now().isoformat() }}`). Because the time is part of the
value, every new value is a new event, even when the rest is the same.

## Talking and guard mode

| Entity | Contents |
|---|---|
| `input_select.lumen_modus` (package) | `normaal`, `bewaking`, `waarschuwing`, `alarm`, `vakantie`, `nacht`, `feest`, `gasten`, `deurbel`. `waarschuwing` and `alarm` turn Lumen red and show the guard bar. |
| `input_text.lumen_melding` (package) | `<time>\|<sentence>`: Lumen says the sentence once. |
| `input_text.lumen_camera` (package) | Camera to show with a warning, e.g. `camera.achtertuin`. |
| `script.lumen_override` / `script.lumen_alarm` (package) | Run by "Bekend, negeren" and "Alarm laten afgaan". Add your siren to `lumen_alarm`. |
| `input_text.lumen_radio` (package) | `<time>\|<stream url>`: starts that stream on the Lumen screen. |

## Doorbell and animals

| Entity | Contents |
|---|---|
| `input_text.lumen_deurbel` (package) | `<time>\|<camera>\|<soort>\|<text>`, with soort `bel`, `persoon`, `pakket` or `dier`. Lumen jumps to that camera: green for the doorbell, amber for an animal. |
| `input_number.lumen_deurbel_geen_antwoord_minuten`, `timer.lumen_deurbel_geen_antwoord` (package) | Optional "nobody answers" flow. |

## Night and away

| Entity | Contents |
|---|---|
| `input_boolean.lumen_nacht_actief`, `input_datetime.lumen_nacht_start`, `input_number.lumen_nacht_wachttijd`, `input_boolean.lumen_nacht_lampen / _airco / _verwarming`, `input_number.lumen_nacht_wintertemp` (package) | Night question "Het huis gaat slapen. Blijf je nog wakker?". Your automation sends that sentence via `lumen_melding`; "Ik blijf wakker" runs `script.lumen_blijf_wakker`. |
| `input_boolean.lumen_niet_thuis` (package) | Away / back home. |
| `input_boolean.lumen_vakantie`, `input_datetime.lumen_vakantie_van / _tot`, `input_number.lumen_vakantie_temp`, `input_boolean.lumen_vakantie_aanwezigheid` (package) | Holiday mode. |

## Garden guard (CCTV page)

| Entity | Contents |
|---|---|
| `input_boolean.lumen_tuin_voor`, `input_boolean.lumen_tuin_achter` (package) | "We are in the front/back garden": your guard automations skip warnings there. |
| `input_boolean.lumen_scherp_achter` (package) | Back garden armed: your automation goes straight to `alarm` on a person. |
| `input_number.lumen_tuin_uren` (package) | Garden mode switches off after this many hours (your automation). |
| `input_text.lumen_cctv_gemarkeerd_camera`, `input_datetime.lumen_cctv_gemarkeerd_tijdstip` (package) | Opens that camera's recording at that moment when the CCTV page opens, until "Gezien". |
| `script.lumen_cctv_export`, `script.lumen_cctv_wis`, `sensor.lumen_cctv_export`, `binary_sensor.lumen_usb_stick` | Optional export to USB and deleting recordings. |

## Energy (Bediening › Energie)

Power in W (or kW), energy in kWh, prices in €/kWh or €/m³. Give these sensors a `state_class`
(`measurement` for power and prices, `total_increasing` for daily counters) so the history pages
can go back months and years.

| Entity | Contents |
|---|---|
| `sensor.lumen_e_zon` | Solar power now (W) |
| `sensor.lumen_e_net` | Grid power: + import, − export (W) |
| `sensor.lumen_e_accu` | Battery power: + charging, − discharging (W) |
| `sensor.lumen_e_accu_pct` | Battery level (%) |
| `sensor.lumen_e_huis` | House consumption (W) |
| `sensor.lumen_e_gas_nu`, `sensor.lumen_e_gas_vandaag` | Gas now (m³/h) and today (m³) |
| `sensor.lumen_e_water_per_dag` | Water per day (L), attributes `laatste_periode`, `jaargemiddelde` |
| `sensor.lumen_e_prijs_nu`, `sensor.lumen_e_gasprijs_nu` | Electricity (€/kWh) and gas (€/m³) price now |
| `sensor.lumen_e_zon_vandaag`, `_verbruik_vandaag`, `_net_af_vandaag`, `_net_terug_vandaag`, `_accu_in_vandaag`, `_accu_uit_vandaag` | Today's totals (kWh) |
| `sensor.lumen_e_kosten_vandaag`, `_kosten_maand`, `_kosten_vorige_maand`, `_besparing_nu`, `_besparing_vandaag`, `_besparing_maand` | Money (€) |
| `sensor.lumen_e_zon_terugverdiend`, `_accu_terugverdiend`, `_totaal_terugverdiend` | Payback (€), attributes `investering`, `percentage`, `verwacht_klaar` |
| `sensor.lumen_e_verwarmen_gas_kosten`, `_verwarmen_airco_kosten`, `_verwarmen_advies` | Cost per kWh of heat, and which is cheaper now |
| `sensor.lumen_e_zon_verwacht_vandaag`, `_morgen` | Solar forecast (kWh), fallback when Forecast.Solar is not in the Energy dashboard |
| `sensor.lumen_e_regeling` | One sentence: what the smart control is doing now |
| `sensor.lumen_klimaat_besluit` | Climate decision per room: attributes keyed by room with `stand`, `setpoint`, `reden` |
| helpers (package) | `input_boolean.lumen_slim_besparen`, `lumen_warmtebuffer`, `lumen_warmtebuffer_prijs`, `input_select.lumen_warmtebuffer_modus / _richting`, `input_select.huis_modus`, comfort and night limits, investments, `input_number.lumen_water_meterstand` + `input_datetime.lumen_water_datum` |

The solar forecast card uses Home Assistant's own forecast (`energy/solar_forecast`): add
Forecast.Solar to the Energy dashboard as the forecast for your solar panels.

## Waste calendar and weather warning

| Entity | Contents |
|---|---|
| `sensor.lumen_afval` | State: next kind (`GFT`, `PMD`, `Papier`, `Restafval`). Attributes `datum` (YYYY-MM-DD), `dagen` (0 today, 1 tomorrow), `lijst` `[{type, datum}]`. The Afvalwijzer integration (HACS) is a good source. |
| `binary_sensor.lumen_weeralarm` | `on` while a warning applies. Attributes `kleur` (`geel`/`oranje`/`rood`), `titel`, `tekst`, `tot`. Meteoalarm (built in) is a good source. |
