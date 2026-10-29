"""Session controls. Only explicit UI actions may trigger these commands."""
import os
import shutil
import subprocess

class SessionError(RuntimeError):
    pass

def command_for(action, which=shutil.which, environ=None):
    env = os.environ if environ is None else environ
    if action == "lock":
        tool = which("loginctl")
        if tool: return [tool, "lock-session"]
        raise SessionError("loginctl is unavailable")
    if action == "logout":
        tool = which("qdbus6")
        if tool: return [tool, "org.kde.Shutdown", "/Shutdown", "logout"]
        tool = which("loginctl")
        session_id = env.get("XDG_SESSION_ID")
        if tool and session_id: return [tool, "terminate-session", session_id]
        raise SessionError("No supported logout handler")
    if action in ("reboot", "poweroff"):
        tool = which("systemctl")
        if tool: return [tool, action]
        raise SessionError("systemctl is unavailable")
    raise SessionError("Unsupported action")

def execute_action(action, which=shutil.which, popen=subprocess.Popen):
    return popen(command_for(action, which=which), start_new_session=True)
