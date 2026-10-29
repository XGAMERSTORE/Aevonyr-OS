# Aevonyr OS roadmap

## 0.8 — Universal Apps (Linux image successfully built)
- Aevonyr Launcher with searchable installed Linux, Flatpak and Waydroid apps.
- Opt-in Flathub and interactive installs, Wine/Waydroid launch paths.
- Timeshift for system snapshots and Back In Time for separate personal backups.
- KDE Eclipse palette and branding.

## 0.9 — Project Eclipse (currently in development)
- First-run wizard in Czech and English (language, network, apps, phone, backup).
- KDE Discover update access with PackageKit, Flatpak and fwupd integration.
- KDE Connect phone pairing, non-sensitive reachability count.
- Better small-screen navigation and Live mode status.
- More thorough image checks for boot records and Linux filesystem.
- Remaining: ISO assembly success, GUI boot and functionality tests.

## 0.9.x — Reliability
- Actual QEMU/VirtualBox boot tests, desktop/login smoke checks and installer tests on disposable virtual disks.
- Snapshot recovery, data-backup restore drills, encrypted disk layouts.
- Hardware/firmware and device driver compatibility testing.
- Better Wine per-application environment management and Waydroid initialization UX.

## 1.0 — Supported OS candidate
- Secure and tested update path; recovery/rollback design.
- Explicit license and redistribution inventory; support lifecycle.
- Accessibility, localization, privacy and security audit.
- User documentation and regular hardware regression tests.

Current Aevonyr uses the **KDE Plasma compositor** rather than a custom standalone Wayland compositor. This is intentional until the Linux distribution is reliable enough.
