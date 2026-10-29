# Aevonyr OS — development roadmap

This roadmap is a plan, not a claim that the features are fully tested.

## 0.8.0 — App Hub, branded launcher and recovery (in development)
- Fullscreen Aevonyr Launcher, integrated into the KDE applications menu.
- Universal App Hub listing installed native, Flatpak and Waydroid apps.
- Optional Flathub integration, per-user interactive installations and KDE Discover Flatpak backend.
- Timeshift system snapshots for installed Linux systems, Back In Time for user data.
- Eclipse KDE color scheme, wallpaper, boot and login presentation.
- Remaining: ISO assembly validation, VirtualBox smoke tests, app installation tests, snapshot/backup recovery.

## 0.9 — Universal compatibility and gaming
- Per-app Wine environments, Bottles integration, logs and application shortcuts.
- Supported Android app store, runtime initialization flow and update actions.
- Steam/Proton integration, graphics driver diagnostics and game compatibility tests.
- KDE Connect integration and more native desktop shell behavior.

## 1.0 — Reliable daily-use release candidate
- Automatic QEMU/VirtualBox boot, desktop and installer smoke tests.
- Tested disk encryption, restore and personal backups on real partition layouts.
- A documented upgrade/update process with tested rollback or recovery strategy.
- Hardware compatibility testing, reliable Wi-Fi, GPU, firmware and power controls.
- Security policy, accessibility, complete translations, licenses and official release support.

Aevonyr 0.8 uses KDE Plasma as its Wayland compositor; developing an independent compositor would be a separate larger project.
