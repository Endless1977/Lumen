# Credits

Lumen's code is MIT licensed (see LICENSE). The 3D model below is **not** covered by that
license; it keeps its own CC BY 4.0 license.

## 3D model

`custom_components/lumen/www/girl_bust.glb`

- **"Girl bust"** by **mariuz_yaphets**
- Source: https://sketchfab.com/3d-models/girl-bust-de07a03f8c4149c0b8cf326ca853a6b8
- License: Creative Commons Attribution 4.0 International (CC BY 4.0), https://creativecommons.org/licenses/by/4.0/
- Changes: converted to GLB with the three.js GLTFExporter. The credit is stored in the file
  (`asset.extras`) and shown by Lumen under the model.

## Libraries and fonts (bundled in `custom_components/lumen/www/vendor/`)

Lumen loads no code from the internet: these files ship with the integration, each with its
license next to it.

| Files | What | License |
|---|---|---|
| `vendor/three.min.js`, `vendor/GLTFLoader.js` | three.js r128, https://threejs.org | MIT (`vendor/LICENSE-three.js.txt`) |
| `vendor/hls.min.js` | hls.js 1.5.13, https://github.com/video-dev/hls.js | Apache License 2.0 (`vendor/LICENSE-hls.js.txt`) |
| `vendor/mediapipe/` | MediaPipe Face Detection 0.4.1646425229 (Google), https://github.com/google/mediapipe | Apache License 2.0 (`vendor/mediapipe/LICENSE.txt`) |
| `vendor/fonts/` | IBM Plex Sans, IBM Plex Mono (IBM) and Oxanium (The Oxanium Project Authors), via Fontsource | SIL Open Font License 1.1 (`vendor/fonts/LICENSE-*.txt`) |

## Services

- Radio search: radio-browser.info (community database, free API)
