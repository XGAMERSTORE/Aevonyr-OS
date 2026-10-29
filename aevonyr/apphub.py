"""Aevonyr Universal App Hub: native apps, Flatpak, and Waydroid.

Only approved executable + argument arrays are launched. Desktop entries are
handed to GIO rather than interpreting their untrusted Exec lines ourselves.
Installing apps is an explicit user action in a visible terminal.
"""
from configparser import ConfigParser, Error as ConfigError
from dataclasses import dataclass
import os
from pathlib import Path
import re
import shutil
import subprocess

APP_ID = re.compile(r"[A-Za-z][A-Za-z0-9_-]*(?:\.[A-Za-z0-9_-]+){2,}")
FLATHUB_URL = "https://dl.flathub.org/repo/flathub.flatpakrepo"

# Suggestions, not an online catalog. Installing always needs user approval.
FEATURED = (
    ("Blender", "org.blender.Blender"),
    ("GIMP", "org.gimp.GIMP"),
    ("Krita", "org.kde.krita"),
    ("LibreOffice", "org.libreoffice.LibreOffice"),
    ("Steam", "com.valvesoftware.Steam"),
)

@dataclass(frozen=True)
class App:
    source: str
    name: str
    identifier: str


class AppHubError(RuntimeError):
    pass


def valid_app_id(value):
    return isinstance(value, str) and len(value) <= 200 and APP_ID.fullmatch(value) is not None


def desktop_roots(environ=None):
    env = os.environ if environ is None else environ
    user_data = env.get("XDG_DATA_HOME") or str(Path.home() / ".local" / "share")
    system_data = env.get("XDG_DATA_DIRS") or "/usr/local/share:/usr/share"
    paths = [Path(user_data)] + [Path(d) for d in system_data.split(":") if d]
    return [base / "applications" for base in paths]


def native_apps(roots=None, cap=450):
    """Enumerate visible XDG desktop entries; user overrides system entries."""
    paths = desktop_roots() if roots is None else roots
    seen = set()
    apps = []
    for root in paths:
        try:
            candidates = sorted(Path(root).glob("*.desktop"))
        except OSError:
            continue
        for path in candidates:
            if path.name in seen:
                continue
            seen.add(path.name)
            try:
                if not path.is_file():
                    continue
                ini = ConfigParser(interpolation=None, strict=False)
                ini.read(path, encoding="utf-8")
                if not ini.has_section("Desktop Entry"):
                    continue
                group = ini["Desktop Entry"]
                # Hidden=true is also a tombstone for a system-wide entry.
                if group.getboolean("Hidden", fallback=False):
                    continue
                if group.getboolean("NoDisplay", fallback=False):
                    continue
                if group.get("Type", "Application") != "Application":
                    continue
                name = group.get("Name", "").strip()
                if not name or len(name) > 100:
                    continue
                apps.append(App("Linux", name, str(path.resolve())))
            except (ConfigError, UnicodeError, OSError, ValueError):
                continue
            if len(apps) >= cap:
                return sorted(apps, key=lambda a: a.name.casefold())
    return sorted(apps, key=lambda a: a.name.casefold())


def _output(command, which=shutil.which, run=subprocess.run, timeout=6):
    executable = which(command[0])
    if not executable:
        return ""
    try:
        result = run([executable, *command[1:]], capture_output=True, text=True,
                     check=False, timeout=timeout)
    except (OSError, UnicodeError, subprocess.TimeoutExpired):
        return ""
    return result.stdout if result.returncode == 0 else ""


def flatpak_apps(which=shutil.which, run=subprocess.run):
    out = _output(["flatpak", "list", "--app", "--columns=application,name"],
                  which=which, run=run)
    apps = []
    for line in out.splitlines()[:350]:
        columns = line.split("\t", 1)
        if len(columns) != 2:
            continue
        identifier, name = columns
        if valid_app_id(identifier) and name.strip():
            apps.append(App("Flatpak", name.strip()[:100], identifier))
    return sorted(apps, key=lambda a: a.name.casefold())


def android_apps(which=shutil.which, run=subprocess.run):
    """Waydroid app list is a block of Name/packageName fields."""
    out = _output(["waydroid", "app", "list"], which=which, run=run)
    apps = []
    name = ""
    for line in (out + "\n\n").splitlines():
        item = line.strip()
        lower = item.lower()
        if lower.startswith("name:"):
            name = item.split(":", 1)[1].strip()
        elif lower.startswith("packagename:"):
            identifier = item.split(":", 1)[1].strip()
            if valid_app_id(identifier):
                apps.append(App("Android", (name or identifier)[:100], identifier))
            name = ""
    return sorted(apps[:200], key=lambda a: a.name.casefold())


def installed_apps(roots=None, which=shutil.which, run=subprocess.run):
    return sorted(
        native_apps(roots) + flatpak_apps(which, run) + android_apps(which, run),
        key=lambda app: (app.name.casefold(), app.source),
    )


def launch_command(app, which=shutil.which):
    if app.source == "Linux":
        target = Path(app.identifier).expanduser()
        if not target.is_file() or target.suffix.lower() != ".desktop":
            raise AppHubError("Desktop launcher not found.")
        launcher = which("gio")
        if launcher:
            return (launcher, "launch", str(target))
        raise AppHubError("GIO desktop launcher is not installed.")
    if app.source in ("Flatpak", "Android"):
        if not valid_app_id(app.identifier):
            raise AppHubError("Invalid application ID.")
        executable = which("flatpak" if app.source == "Flatpak" else "waydroid")
        if not executable:
            raise AppHubError(f"{app.source} runtime is not installed.")
        if app.source == "Flatpak":
            return (executable, "run", app.identifier)
        return (executable, "app", "launch", app.identifier)
    raise AppHubError("Unsupported application type.")


def _terminal_plan(arguments, which=shutil.which):
    console = which("konsole")
    if not console:
        raise AppHubError("Konsole is needed for interactive installation.")
    return (console, "--hold", "-e", *arguments)


def enable_flathub_command(which=shutil.which):
    binary = which("flatpak")
    if not binary:
        raise AppHubError("Flatpak is not installed.")
    return _terminal_plan(
        (binary, "remote-add", "--user", "--if-not-exists", "flathub", FLATHUB_URL), which
    )


def install_flatpak_command(identifier, which=shutil.which):
    if not valid_app_id(identifier):
        raise AppHubError("Invalid Flatpak application ID.")
    binary = which("flatpak")
    if not binary:
        raise AppHubError("Flatpak is not installed.")
    # Interactive terminal: Flatpak itself asks before downloads/permissions.
    return _terminal_plan((binary, "--user", "install", "flathub", identifier), which)


def start(command, popen=subprocess.Popen):
    return popen(list(command), start_new_session=True)
