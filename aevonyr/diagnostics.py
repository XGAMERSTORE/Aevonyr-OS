"""Read-only local diagnostics. Does not collect passwords or alter system settings."""
import os
from pathlib import Path
import platform
import shutil
import subprocess
from .compat import backend_status
from .network import network_status

def android_state(which=shutil.which, run=subprocess.run, environ=None):
    env = os.environ if environ is None else environ
    tool = which("waydroid")
    if not tool:
        return "Not installed"
    if env.get("XDG_SESSION_TYPE", "").lower() != "wayland" and not env.get("WAYLAND_DISPLAY"):
        return "Wayland session required"
    try:
        result = run([tool, "status"], capture_output=True, text=True, timeout=5, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return "Status unavailable"
    if result.returncode:
        return "Not initialized or unavailable"
    info = result.stdout.lower()
    if "session: running" in info and "container: running" in info:
        return "Running"
    if "session: stopped" in info or "container: stopped" in info:
        return "Stopped"
    return "Installed, not running"

def live_mode(path=Path("/proc/cmdline")):
    try:
        return "Live" if "boot=live" in path.read_text(encoding="utf-8").split() else "Installed / other"
    except OSError:
        return "Unknown"

def diagnose(which=shutil.which, run=subprocess.run):
    available = backend_status(which=which)
    try:
        free = round(shutil.disk_usage(Path.home()).free / 1024**3, 1)
    except OSError:
        free = "Unknown"
    return {
        "Aevonyr OS": "0.7.2 Linux",
        "Linux kernel": platform.release(),
        "Session": os.environ.get("XDG_SESSION_TYPE") or "Unknown",
        "Boot mode": live_mode(),
        "Internet connectivity": network_status(which=which, run=run),
        "Wine": "Installed" if available["wine"] else "Not installed",
        "Android / Waydroid": android_state(which=which, run=run),
        "Free disk (GiB)": free
    }

def format_report(status):
    return "\n".join(f"{key}: {value}" for key,value in status.items())
