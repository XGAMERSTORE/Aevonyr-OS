"""User-local preferences and notes; never writes into system folders."""
import json
import os
from pathlib import Path
from .i18n import normalize_language

def config_dir():
    return Path(os.environ.get("XDG_CONFIG_HOME") or (Path.home() / ".config")) / "aevonyr-os"

def data_dir():
    return Path(os.environ.get("XDG_DATA_HOME") or (Path.home() / ".local" / "share")) / "aevonyr-os"

def load_preferences():
    try:
        data = json.loads((config_dir() / "settings.json").read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        data = {}
    return {"language": normalize_language(data.get("language", "en"))}

def save_preferences(preferences):
    directory = config_dir()
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / "settings.json"
    temporary = target.with_suffix(".tmp")
    temporary.write_text(json.dumps({"language": normalize_language(preferences.get("language"))}, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(target)

def notes_path():
    return data_dir() / "notes.txt"
