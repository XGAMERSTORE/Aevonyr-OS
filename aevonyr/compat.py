"""Plan Wine and Waydroid commands safely. No shell=True."""
from dataclasses import dataclass
from pathlib import Path
import os
import shutil
import subprocess

class CompatibilityError(RuntimeError):
    pass

@dataclass(frozen=True)
class LaunchPlan:
    kind: str
    command: tuple

def backend_status(which=shutil.which):
    return {
        "wine": bool(which("wine")),
        "waydroid": bool(which("waydroid")),
        "wayland": os.environ.get("XDG_SESSION_TYPE", "").lower() == "wayland" or bool(os.environ.get("WAYLAND_DISPLAY")),
    }

def make_plan(filename, which=shutil.which):
    path = Path(filename).expanduser().resolve()
    if not path.is_file():
        raise CompatibilityError(f"File not found: {path}")
    extension = path.suffix.lower()
    if extension in (".exe", ".msi"):
        executable = which("wine")
        if not executable:
            raise CompatibilityError("Wine is not installed. Install Wine before running Windows applications.")
        if extension == ".msi":
            return LaunchPlan("msi", (executable, "msiexec", "/i", str(path)))
        return LaunchPlan("exe", (executable, str(path)))
    if extension == ".apk":
        executable = which("waydroid")
        if not executable:
            raise CompatibilityError("Waydroid is not installed. Initialize it in a Wayland session.")
        return LaunchPlan("apk-install", (executable, "app", "install", str(path)))
    raise CompatibilityError("Unsupported file format. Select an EXE, MSI or APK.")

def execute_plan(plan, popen=subprocess.Popen):
    return popen(list(plan.command), start_new_session=True)

def open_android(which=shutil.which, popen=subprocess.Popen):
    program = which("waydroid")
    if not program:
        raise CompatibilityError("Waydroid is not installed.")
    return popen([program, "show-full-ui"], start_new_session=True)
