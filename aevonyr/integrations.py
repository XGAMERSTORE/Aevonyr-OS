"""Whitelisted KDE integrations, without shell commands or silent modifications."""
from dataclasses import dataclass
import shutil
import subprocess


class IntegrationError(RuntimeError):
    pass


@dataclass(frozen=True)
class Tool:
    name: str
    candidates: tuple
    purpose: str


TOOLS = {
    "updates": Tool("KDE Discover", ("plasma-discover",), "Software and updates"),
    "phone": Tool("KDE Connect", ("kdeconnect-settings", "kdeconnect-app"),
                  "Pair a phone on the local network"),
    "settings": Tool("System Settings", ("systemsettings",), "Desktop settings"),
    "files": Tool("Dolphin", ("dolphin",), "Files and folders"),
    "backup": Tool("Back In Time", ("backintime-qt",), "Personal file backups"),
}


def tool_command(key, which=shutil.which):
    item = TOOLS.get(key)
    if item is None:
        raise IntegrationError("Unknown system tool.")
    for name in item.candidates:
        binary = which(name)
        if binary:
            return (binary,)
    raise IntegrationError(f"{item.name} is not installed.")


def available_tools(which=shutil.which):
    return {key: any(bool(which(candidate)) for candidate in spec.candidates)
            for key, spec in TOOLS.items()}


def start_tool(key, which=shutil.which, popen=subprocess.Popen):
    return popen(list(tool_command(key, which=which)), start_new_session=True)


def paired_device_count(which=shutil.which, run=subprocess.run):
    """Only count paired KDE Connect devices; never expose device IDs."""
    binary = which("kdeconnect-cli")
    if not binary:
        return None
    try:
        response = run([binary, "--list-devices", "--id-only"], capture_output=True,
                       text=True, timeout=6, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if response.returncode:
        return None
    return sum(
        1 for line in response.stdout.splitlines()
        if line.strip() and not line.strip().lower().startswith("no device")
    )
