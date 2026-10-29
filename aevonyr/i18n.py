"""English-first translations with validated user-installed JSON language packs."""
import json
import os
from pathlib import Path
import re

CATALOG = json.loads(Path(__file__).with_name("locales.json").read_text(encoding="utf-8"))
LANGUAGES = {
    "en": "English", "cs": "Čeština", "sk": "Slovenčina",
    "de": "Deutsch", "pl": "Polski", "fr": "Français",
    "es": "Español", "it": "Italiano", "pt": "Português",
    "uk": "Українська"
}
_LOCALE = re.compile(r"^[a-z]{2,3}(?:-[a-z0-9]{2,8}){0,3}$")
_KEY = re.compile(r"^[a-z][a-z0-9_]{0,79}$")
_MAX_BYTES = 256 * 1024


def language_pack_dir():
    root = os.environ.get("XDG_DATA_HOME")
    return (Path(root) if root else Path.home() / ".local" / "share") / "aevonyr-os" / "languages"


def normalize_language(code):
    code = str(code or "en").strip().replace("_", "-").lower()
    if code in CATALOG:
        return code
    base = code.split("-", 1)[0]
    return base if base in CATALOG else "en"


def tr(key, language="en"):
    code = normalize_language(language)
    return CATALOG.get(code, {}).get(key) or CATALOG["en"].get(key) or key


def missing_keys(language):
    code = normalize_language(language)
    return sorted(key for key in CATALOG["en"] if not CATALOG[code].get(key))


def _read_pack(source):
    path = Path(source).expanduser()
    if path.suffix.lower() != ".json":
        raise ValueError("Language pack must be JSON.")
    if path.stat().st_size > _MAX_BYTES:
        raise ValueError("Language pack exceeds 256 KiB.")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Language pack must be a JSON object.")
    locale = data.get("locale")
    name = data.get("name")
    strings = data.get("strings")
    if not isinstance(locale, str):
        raise ValueError("Missing locale code.")
    locale = locale.replace("_", "-").lower()
    if not _LOCALE.fullmatch(locale) or locale == "en":
        raise ValueError("Invalid locale code or protected base English.")
    if not isinstance(name, str) or not 1 <= len(name.strip()) <= 60:
        raise ValueError("Invalid language name.")
    if not isinstance(strings, dict) or len(strings) > 1500:
        raise ValueError("Invalid translation dictionary.")
    if not all(isinstance(k, str) and _KEY.fullmatch(k) and
               isinstance(v, str) and len(v) <= 4096 for k, v in strings.items()):
        raise ValueError("Invalid translation entries.")
    return locale, name.strip(), strings, data


def _register(locale, name, strings):
    CATALOG[locale] = {**CATALOG.get(locale, {}), **strings}
    if locale not in LANGUAGES:
        LANGUAGES[locale] = f"{name} ({locale})"


def load_language_packs(directory=None):
    directory = Path(directory) if directory is not None else language_pack_dir()
    loaded = []
    if not directory.is_dir():
        return loaded
    for path in sorted(directory.glob("*.json")):
        try:
            locale, name, strings, _ = _read_pack(path)
            _register(locale, name, strings)
            loaded.append(locale)
        except (OSError, UnicodeError, ValueError, TypeError):
            continue
    return loaded


def install_language_pack(source, directory=None):
    locale, name, strings, data = _read_pack(source)
    directory = Path(directory) if directory is not None else language_pack_dir()
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / (locale + ".json")
    temporary = target.with_name(target.name + ".tmp")
    try:
        temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        temporary.replace(target)
    finally:
        temporary.unlink(missing_ok=True)
    _register(locale, name, strings)
    return locale


load_language_packs()
