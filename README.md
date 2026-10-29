# Aevonyr OS

**One System. Two Worlds.**

Aevonyr OS is a custom desktop project with an English-first interface, multilingual localization, and integrations for Windows and Android application compatibility.

> Development status: This repository currently contains a functional **Python/Tk desktop app that runs inside an existing Linux session**, not yet a standalone operating system or a bootable installer ISO. The older LumaOS UEFI previews are separate prototypes and do not support Wine or Android.

## Features

- English is the default UI language. Settings can switch immediately between 10 starter languages: English, Czech, Slovak, German, Polish, French, Spanish, Italian, Portuguese, and Ukrainian.
- Language packs are intentionally at different stages of completion; missing strings fall back to English.
- Dark-violet desktop shell with navigation, a file browser, persistent notes and runtime status.
- Optional Wine integration for Windows EXE/MSI launch, if Wine is installed.
- Optional Waydroid integration for Android APK installation, if Waydroid is installed, initialized and running in Wayland.
- Confirmation before running selected Windows apps or installing Android APKs.

## Run it on an existing Linux desktop

Use Python 3.10+ and Tkinter. On Debian or Ubuntu install Python and Tkinter using your package manager (for example: sudo apt install python3 python3-tk).

Clone this repository and open a terminal in its root directory, then run:

    python3 -m aevonyr

To see which compatibility backends are installed:

    python3 -m aevonyr --check

To launch a Windows executable or install an APK from a terminal:

    python3 -m aevonyr --launch /path/to/file.exe

APK installation is not the same as launching the Android app. You can open Waydroid from the Aevonyr Applications page. Not every Windows or Android application will work on Linux x86-64.

## Structure

- aevonyr/ui.py: graphical preview shell, file browser, notes, settings
- aevonyr/compat.py: safe Wine/Waydroid subprocess integration
- aevonyr/i18n.py and aevonyr/locales.json: translation foundation
- aevonyr/config.py: user preferences and notes storage
- tests: regression tests for translation and compatibility
- docs: roadmap and integration guidelines

Tests:

    python3 -m unittest discover -s tests -v
    python3 -m compileall -q aevonyr

## Third-party components and licensing

Aevonyr OS does not contain Wine or Waydroid source code or binaries, proprietary Microsoft or Google components, or an Android runtime. Wine and Waydroid belong to their respective upstream projects. Packaging them into a public ISO requires observing their respective license terms and providing appropriate notices. The repository owner will select the license for original Aevonyr source prior to public release.

See docs/ROADMAP.md for the ISO milestone.
