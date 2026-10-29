"""Use established system restore and personal backup tools, safely.

Timeshift restores system files (not personal documents), and requires a
configured installed system. Back In Time is the personal-data backup tool.
Aevonyr never automatically snapshots/restores partitions or selects disks.
"""
from pathlib import Path
import shutil
import subprocess


class RestoreError(RuntimeError):
    pass


def is_live_boot(path=Path("/proc/cmdline")):
    try:
        return "boot=live" in path.read_text(encoding="utf-8").split()
    except OSError:
        return False


def restore_command(which=shutil.which, is_live=None):
    live = is_live_boot() if is_live is None else is_live
    if live:
        raise RestoreError("System snapshots are unavailable in Live mode. Install Aevonyr first.")
    tool = which("timeshift-launcher")
    if not tool:
        raise RestoreError("Timeshift is not installed.")
    return (tool,)


def backup_command(which=shutil.which):
    tool = which("backintime-qt")
    if not tool:
        raise RestoreError("Back In Time is not installed.")
    return (tool,)


def start_tool(command, popen=subprocess.Popen):
    return popen(list(command), start_new_session=True)
