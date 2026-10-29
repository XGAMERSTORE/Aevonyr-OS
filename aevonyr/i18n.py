"""English-first translations with per-key fallback and live language switching."""
import json
from pathlib import Path

CATALOG = json.loads(Path(__file__).with_name("locales.json").read_text(encoding="utf-8"))
LANGUAGES = {
    "en": "English", "cs": "Čeština", "sk": "Slovenčina",
    "de": "Deutsch", "pl": "Polski", "fr": "Français",
    "es": "Español", "it": "Italiano", "pt": "Português", "uk": "Українська"
}

def normalize_language(code):
    code = (code or "en").replace("_", "-").split("-", 1)[0].lower()
    return code if code in CATALOG else "en"

def tr(key, language="en"):
    code = normalize_language(language)
    return CATALOG.get(code, {}).get(key) or CATALOG["en"].get(key) or key

def missing_keys(language):
    code = normalize_language(language)
    return sorted(set(CATALOG["en"]) - set(CATALOG[code]))
