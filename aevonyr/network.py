"""Read real NetworkManager connectivity. Credentials remain in system settings."""
import shutil
import subprocess

def network_status(which=shutil.which, run=subprocess.run):
    binary = which("nmcli")
    if not binary:
        return "unavailable"
    try:
        result = run([binary, "-t", "-f", "CONNECTIVITY", "general"],
                     capture_output=True, text=True, timeout=4, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return "unavailable"
    if result.returncode:
        return "unavailable"
    lines = result.stdout.strip().splitlines()
    value = lines[0].strip().lower() if lines else ""
    return value if value in ("full", "limited", "portal", "none", "unknown") else "unavailable"

def open_network_settings(which=shutil.which, popen=subprocess.Popen):
    editor = which("nm-connection-editor")
    if editor:
        return popen([editor], start_new_session=True)
    settings = which("systemsettings")
    if settings:
        return popen([settings, "kcm_networkmanagement"], start_new_session=True)
    raise RuntimeError("Network settings application is not installed.")
