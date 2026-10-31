"""Constants for the Lumen integration."""

DOMAIN = "lumen"
VERSION = "2026.10.31"

# Where the page and the bundled model are served from (same origin as Home Assistant,
# so Lumen can use the existing Home Assistant login and needs no access token).
URL_BASE = "/lumen_static"
PANEL_URL_PATH = "lumen"

CONF_TITLE = "title"
CONF_ICON = "icon"
CONF_ADMIN_ONLY = "admin_only"
CONF_AGENT = "agent"
CONF_TTS = "tts"
CONF_VOICE = "voice"
CONF_STT = "stt"
CONF_LANG = "lang"
CONF_PLACE = "place"

DEFAULT_TITLE = "Lumen"
DEFAULT_ICON = "mdi:face-recognition"

# Options that are handed to the page in its URL. The page only uses them when the
# browser has no setting of its own for that field (local settings always win).
PAGE_OPTIONS = (CONF_AGENT, CONF_TTS, CONF_VOICE, CONF_STT, CONF_LANG, CONF_PLACE)
