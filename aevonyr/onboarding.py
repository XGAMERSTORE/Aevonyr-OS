"""First-run state for Aevonyr OS.

No account details, passwords, device IDs or network credentials are stored.
Completion is an explicit user action. An interrupted wizard returns next login.
"""
import json
import os
from pathlib import Path


def onboarding_state_path(environ=None, home=None):
    env = os.environ if environ is None else environ
    root = env.get("XDG_CONFIG_HOME")
    if root:
        config = Path(root).expanduser()
    else:
        config = (Path.home() if home is None else Path(home)) / ".config"
    return config / "aevonyr-os" / "welcome-state.json"


def completed(path=None):
    source = onboarding_state_path() if path is None else Path(path)
    try:
        data = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeError):
        return False
    return isinstance(data, dict) and data.get("completed") is True


def mark_completed(path=None):
    source = onboarding_state_path() if path is None else Path(path)
    source.parent.mkdir(parents=True, exist_ok=True)
    tmp = source.with_name(source.name + ".tmp")
    try:
        # Atomic replace keeps an incomplete write from confusing the wizard.
        tmp.write_text('{"completed": true}\n', encoding="utf-8")
        tmp.replace(source)
    finally:
        tmp.unlink(missing_ok=True)
