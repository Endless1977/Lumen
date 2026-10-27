# Lumen

**A holographic, talking assistant for Home Assistant.** Lumen draws a 3D face as a laser
hologram, listens and speaks through your Home Assistant voice pipeline, and gives you one
screen for your house: climate, lights, energy, media and cameras.

> 🇳🇱 Lumen is written in Dutch (screens and voice). See [Nederlands](#nederlands) below.

![Lumen: the hologram face with the house panel and the chat](https://raw.githubusercontent.com/Endless1977/Lumen/main/docs/screenshots/1-lumen.jpg)

<details>
<summary><b>More screenshots</b></summary>

| | |
|---|---|
| ![Climate per room](https://raw.githubusercontent.com/Endless1977/Lumen/main/docs/screenshots/2-klimaat.png) | ![Energy flow and today's totals](https://raw.githubusercontent.com/Endless1977/Lumen/main/docs/screenshots/4-energie.png) |
| **Bediening › Klimaat**: every thermostat and air conditioner | **Bediening › Energie**: live flow between solar, grid, battery, house, gas and water |
| ![Energy history per month](https://raw.githubusercontent.com/Endless1977/Lumen/main/docs/screenshots/5-historie.png) | ![CCTV with the garden guard](https://raw.githubusercontent.com/Endless1977/Lumen/main/docs/screenshots/6-cctv.png) |
| **History**: tap any chart, page back per day, week, month or year | **CCTV**: all cameras live, garden guard on top |
| ![Media](https://raw.githubusercontent.com/Endless1977/Lumen/main/docs/screenshots/7-media.png) | ![Model, calibration and look](https://raw.githubusercontent.com/Endless1977/Lumen/main/docs/screenshots/8-weergave.jpg) |
| **Media**: radio, library and every speaker in Home Assistant | **Weergave**: choose a model, set eyes and mouth, colour and light |

</details>

*Screenshots use demo data.*

## What it does

- **Hologram face**: a 3D bust built up from laser lines, with eyes that follow you and a
  mouth that moves with the voice. Bring your own `.glb` models and calibrate eyes and mouth
  on the page.
- **Talk to your house**: uses your Home Assistant conversation agent (Ollama, OpenAI, the
  built-in one, …), text-to-speech (Piper, cloud voices) and speech-to-text (Whisper), or the
  browser's own voice and speech recognition.
- **Huis**: your house as a 3D hologram (optional model) with live room status.
- **Bediening**: climate, lights per room, switches, and an **energy** page with a live flow
  diagram (solar, grid, battery, gas, water), history per day, week, month and year, solar
  forecast, costs and savings.
- **Media**: radio (radio-browser.info), your Home Assistant media library and any media player
  (Sonos, Cast, Music Assistant, …); TVs with apps and a remote pad.
- **CCTV**: all cameras live (WebRTC, HLS fallback), one camera large with its own controls,
  continuous playback of recordings, export, talk-back where the camera supports it.
- **Guard mode**, **night question**, **doorbell** and **animal at the door** banners, weather
  warnings and the waste calendar, all driven by Home Assistant helpers.
- **Raspberry Pi status** (CPU, temperature, memory, disk) on every page.

Every feature is optional: when the entities it needs are missing, Lumen simply hides it.

## Install

### HACS (custom repository)

1. HACS › ⋮ › **Custom repositories** › add `https://github.com/Endless1977/Lumen`, type **Integration**.
   (Once Lumen is in the HACS default list, just search for **Lumen** in HACS.)
2. Install **Lumen**, then restart Home Assistant.
3. **Settings › Devices & services › Add integration › Lumen.** Pick the conversation agent,
   voice and speech recognition (all optional) and your language.
4. **Lumen** appears in the sidebar.

### Manual

Copy `custom_components/lumen` into `/config/custom_components/`, restart, and add the
integration as above.

### Helpers (recommended)

Lumen reads and writes a set of helpers (mode, announcements, doorbell, night mode, garden
guard, heat buffer, …). The easiest way to create them all is the package
[`packages/lumen.yaml`](packages/lumen.yaml):

```yaml
# configuration.yaml
homeassistant:
  packages: !include_dir_named packages
```

Copy `lumen.yaml` to `/config/packages/` and restart. Delete what you don't need.

### Blueprints

| Blueprint | What it does |
|---|---|
| [Doorbell](blueprints/automation/lumen/deurbel.yaml) | Doorbell pressed → Lumen glows green and shows the doorbell camera |
| [Animal at the door](blueprints/automation/lumen/dier.yaml) | Camera sees an animal → Lumen glows amber and shows that camera (never an alarm) |
| [Let Lumen say something](blueprints/automation/lumen/melding.yaml) | An entity changes → Lumen speaks your sentence |
| [Warning back to normal](blueprints/automation/lumen/waarschuwing_terug.yaml) | A guard warning returns to normal after N minutes without a reaction; an alarm never does |

Import them via **Settings › Automations › Blueprints › Import blueprint** with the file's GitHub URL.

### Your own data

The energy page, waste calendar, weather warning and climate decisions show sensors that
depend on your own devices (`sensor.lumen_e_*`, `sensor.lumen_afval`,
`binary_sensor.lumen_weeralarm`, …). [docs/entities.md](docs/entities.md) describes what each
one should contain, so you can make them with template sensors.

## Settings on the page

Each screen keeps its own settings (Lumen › **Instellingen**): Home Assistant address, voice,
models, which entities to show, radio stations, room and camera names. What you choose in the
integration is only the default for screens that have no setting of their own.

**3D models**: `girl_bust.glb` is included. Put your own models in `/config/www/` and list them
as `/local/your_model.glb`. The 3D house model is optional (`/local/lumen/house.glb` by default).

## Security and privacy

- Lumen runs inside Home Assistant (same address), so it uses your normal Home Assistant login.
  **You don't need a long-lived access token.** Never put a token in a file under `/config/www`:
  that folder is public.
- Camera images and microphone audio stay between your browser and your Home Assistant.
  The microphone is only used while you talk to Lumen or hold the talk button.
- External resources: three.js and hls.js (jsDelivr / cdnjs), Google Fonts, and
  radio-browser.info when you search for radio stations.

## Requirements

- Home Assistant 2024.12 or newer
- A modern browser (Chrome, Edge, Safari, Firefox); a tablet works well as a wall screen
- Optional: a conversation agent, Piper/Whisper or cloud voices, Frigate or another recorder for playback

## Credits

- 3D model **"Girl bust"** by [mariuz_yaphets](https://sketchfab.com/3d-models/girl-bust-de07a03f8c4149c0b8cf326ca853a6b8),
  licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) (converted to GLB).
- [three.js](https://threejs.org) (MIT), [hls.js](https://github.com/video-dev/hls.js) (Apache-2.0),
  fonts IBM Plex and Oxanium (SIL Open Font License).

See [CREDITS.md](CREDITS.md). Lumen itself is MIT licensed, see [LICENSE](LICENSE).

---

## Nederlands

Lumen is een holografisch, pratend hoofd voor Home Assistant: één scherm om met je huis te
praten en het te bedienen (klimaat, verlichting, energie, media, camera's).

**Installeren:** HACS › ⋮ › Aangepaste repositories › `https://github.com/Endless1977/Lumen` (type
Integratie) › Lumen installeren › Home Assistant herstarten › Instellingen › Apparaten & diensten ›
Integratie toevoegen › Lumen. Lumen staat daarna in de zijbalk. Een token is niet nodig.

**Helpers:** zet [`packages/lumen.yaml`](packages/lumen.yaml) in `/config/packages/` (zie hierboven)
en herstart. **Blueprints** voor de deurbel, een dier bij de deur, meldingen en het terugzetten van
een waarschuwing staan in `blueprints/automation/lumen/`. Wat de energie-, afval- en weersensoren
moeten bevatten staat in [docs/entities.md](docs/entities.md).
