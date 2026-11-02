"""File-manager package integration. Argument arrays only; never elevate apps."""
from pathlib import Path
import os
import re
import shutil
import subprocess
import time
from .compat import CompatibilityError, make_plan


def package_command(filename, which=shutil.which):
    path = Path(filename).expanduser().resolve()
    if not path.is_file():
        raise CompatibilityError(f'File not found: {path}')
    if path.suffix.lower() == '.deb':
        program = which('plasma-discover')
        if not program:
            raise CompatibilityError('Software Center is not installed.')
        return (program, '--local-filename', str(path))
    return make_plan(path, which=which).command


def checked(command, timeout=120, run=subprocess.run):
    result = run(list(command), capture_output=True, text=True, timeout=timeout,
                 env={**os.environ, 'LC_ALL': 'C'})
    if result.returncode:
        detail = (result.stderr or result.stdout or 'No details returned').strip()
        raise CompatibilityError(detail[-2500:])
    return result.stdout


def apk_package_id(filename, which=shutil.which, run=subprocess.run):
    aapt = which('aapt')
    if not aapt:
        raise CompatibilityError('Android package reader (aapt) is not installed.')
    output = checked([aapt, 'dump', 'badging', str(Path(filename).resolve())], 30, run)
    match = re.search(r"^package: name='([A-Za-z0-9_]+(?:\.[A-Za-z0-9_]+)+)'", output, re.M)
    if not match:
        raise CompatibilityError('This APK has no readable Android package identifier.')
    return match.group(1)


def install_apk(filename, progress=lambda _: None, which=shutil.which,
                run=subprocess.run, popen=subprocess.Popen, sleep=time.sleep):
    # Validate before starting any runtime or installing anything.
    command = package_command(filename, which)
    package = apk_package_id(filename, which, run)
    if not (os.environ.get('WAYLAND_DISPLAY') or os.environ.get('XDG_SESSION_TYPE') == 'wayland'):
        raise CompatibilityError('Android needs a Wayland desktop session. Log out and choose Plasma (Wayland).')
    if not Path('/var/lib/waydroid/waydroid.cfg').is_file():
        raise CompatibilityError('Android needs a one-time setup. Choose Set up Android, then open this APK again.')
    waydroid = command[0]
    progress('Starting Android…')
    status = checked([waydroid, 'status'], 15, run)
    if not re.search(r'Session:\s+RUNNING', status):
        popen([waydroid, 'session', 'start'], stdout=subprocess.DEVNULL,
              stderr=subprocess.DEVNULL, start_new_session=True)
    for _ in range(60):
        status = checked([waydroid, 'status'], 15, run)
        if re.search(r'Session:\s+RUNNING', status) and re.search(r'Container:\s+RUNNING', status):
            break
        sleep(1)
    else:
        raise CompatibilityError('Android did not start. Use Set up Android and check the container service.')
    progress('Installing Android application…')
    output = checked(command, 180, run)
    # Some runtime versions report Android package-manager failures in output.
    if re.search(r'INSTALL_FAILED|Failure \[|Failed to install', output, re.I):
        raise CompatibilityError(output[-2500:])
    apps = checked([waydroid, 'app', 'list'], 30, run)
    if not re.search(r'^\s*packageName:\s*' + re.escape(package) + r'\s*$', apps, re.M | re.I):
        raise CompatibilityError('Android did not confirm this application was installed.')
    return package
