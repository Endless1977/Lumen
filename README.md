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
| ![The example house as a hologram](https://raw.githubusercontent.com/Endless1977/Lumen/main/docs/screenshots/3-huis.jpg) | ![Climate per room](https://raw.githubusercontent.com/Endless1977/Lumen/main/docs/screenshots/2-klimaat.png) |
| **Huis**: the included example house, per floor; tap a room for its status | **Bediening › Klimaat**: every thermostat and air conditioner |
| ![Energy flow and today's totals](https://raw.githubusercontent.com/Endless1977/Lumen/main/docs/screenshots/4-energie.png) | ![Energy history per month](https://raw.githubusercontent.com/Endless1977/Lumen/main/docs/screenshots/5-historie.png) |
| **Bediening › Energie**: live flow between solar, grid, battery, house, gas and water | **History**: tap any chart, page back per day, week, month or year |
| ![CCTV with the garden guard](https://raw.githubusercontent.com/Endless1977/Lumen/main/docs/screenshots/6-cctv.png) | ![Media](https://raw.githubusercontent.com/Endless1977/Lumen/main/docs/screenshots/7-media.png) |
| **CCTV**: all cameras live, garden guard on top | **Media**: radio, library and every speaker in Home Assistant |
| ![Model, calibration and look](https://raw.githubusercontent.com/Endless1977/Lumen/main/docs/screenshots/8-weergave.jpg) | |
| **Weergave**: choose a model, set eyes and mouth, colour and light | |
</details>

*Screenshots use demo data.*

## What it does

- **Hologram face**: a 3D bust built up from laser lines, with eyes that follow you and a
  mouth that moves with the voice. Bring your own `.glb` models and calibrate eyes and mouth
  on the page.
- **Talk to your house**: uses your Home Assistant conversation agent (Ollama, OpenAI, the
  built-in one, …), text-to-speech (Piper, cloud voices) and speech-to-text (Whisper), or the
  browser's own voice and speech recognition.
- **Huis**: your house as a 3D hologram with live room status, per floor. An example house is
  included, so you can see it working straight away; swap in your own model when you have one
  (see [The 3D house](#the-3d-house)).
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
- **Expressive face with shape keys**: give a model mouth shapes, blinking and moods with the
  included [face editor](#face-editor-shape-keys); Lumen uses them while talking, listening and thinking.
- **Screens in Dutch, English, German and French** (Lumen › Instellingen › Schermtaal).

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
as `/local/your_model.glb`.

### The 3D house

![The example house in the Huis tab](https://raw.githubusercontent.com/Endless1977/Lumen/main/docs/screenshots/3-huis.jpg)

Lumen comes with an **example house** (`house.glb`): two floors, an attic and a garden with
rooms, a driveway gate, solar panels, a heat pump, an EV charger and a robot mower. It is shown
when the field **Instellingen › Huismodel** is empty. Use the floor buttons on the left, drag to
turn, pinch or scroll to zoom and tap a room to see its status.

To use **your own house**, put the `.glb` in `/config/www/` and enter `/local/my_house.glb` under
**Instellingen › Huismodel**. Lumen reads rooms, floors and devices from the model itself
(floorplan3d format): nodes carry `extras.fp` with

| Field | Meaning |
|---|---|
| `kind` | `level` (a floor), `room`, `zone` (garden, driveway) or `object` (a device) |
| `id`, `label` | identifier and the name shown on screen |
| `type` | for objects: `light`, `climate`, `gate`, `solar`, `ev_charger`, `mower`, … |
| `layer` | what a mesh is (`facade`, `roof`, `glass`, `furniture`, …), used to fade parts per floor |
| `suggest` | the Home Assistant entity (`light.kitchen`) or area it belongs to |

The example house uses generic names such as `light.kitchen` and `climate.living_room`; rooms
and devices whose entity is not in your Home Assistant just show no status.

## Face editor (shape keys)

[`tools/gezicht-editor.html`](tools/gezicht-editor.html) is a stand-alone page: download it and
open it in Chrome or Edge on your computer (it needs internet for three.js).

1. Load the head model (`.glb`), and optionally a second `.glb` with eyeballs and the inside of
   a mouth (teeth, gums). Choose per part whether it is the left eye, the right eye or the mouth.
2. Click around the **outline of the lips**, then along the **line between the lips** from corner
   to corner. Your clicks become a smooth line; drag a handle or the line itself to adjust it.
3. Click the middle of each **eye**. Eyeballs already in the model are found and matched
   (*Oogbollen in het model zoeken*); otherwise set the eyeball size, depth and eye opening yourself.
   **Röntgen** (x-ray) lets you look through the skin.
4. **Make shapes** creates 16 shape keys: `mond_a`, `mond_e`, `mond_i`, `mond_o`, `mond_u`,
   `mond_m`, `mond_f`, `knipper`, `knipoog_links`, `knipoog_rechts`, `ogen_smal`, `lach`,
   `verdriet`, `verbazing`, `boos`, `wenkbrauwen_op`. Test them with sliders, the talk test and blink.
5. **Save model** gives a `.glb` with the shape keys. Put it in `/config/www/` and add it in
   Lumen › Instellingen › 3D-modellen.

Any model whose shape keys use these names works, also one made in Blender. Keep the licence of
models you use in mind before sharing them.

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

**Huis:** een voorbeeldhuis zit erbij en wordt getoond zolang Instellingen › Huismodel leeg is.
Je eigen model zet je in `/config/www/` en vul je in als `/local/mijn_huis.glb`.

**Helpers:** zet [`packages/lumen.yaml`](packages/lumen.yaml) in `/config/packages/` (zie hierboven)
en herstart. **Blueprints** voor de deurbel, een dier bij de deur, meldingen en het terugzetten van
een waarschuwing staan in `blueprints/automation/lumen/`. Wat de energie-, afval- en weersensoren
moeten bevatten staat in [docs/entities.md](docs/entities.md).
