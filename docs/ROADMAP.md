# Aevonyr OS — development roadmap

## 0.5: desktop foundation
- English as the default language.
- 10 starter languages, runtime switching, English fallback for incomplete translations.
- Live desktop shell on top of an existing Linux graphical session.
- Functional file browser and saved notes.
- Wine EXE/MSI and Waydroid APK integrations when third-party runtimes are installed.
- Python unit tests and continuous integration.

## 0.6: modern native desktop
- A real window compositor, desktop windows, shortcuts, notifications and app management.
- Full translation QA, UI typography, RTL script support, keyboard accessibility.
- Better Wine environment configuration and Android package discovery.

## 0.7: bootable Aevonyr Live ISO
- Linux kernel, filesystem, hardware drivers and package management.
- Wayland compositor, application shell, system updates.
- Distribution packaging of Wine, honoring upstream redistribution rights.
- Optional Waydroid with kernel binder support, initialized Android image and Wayland.
- UEFI/BIOS boot, installer design, QEMU/VirtualBox/physical machine tests.

## 1.0: candidate distribution
- Security/update policy, test infrastructure, driver/device support.
- Per-application sandboxing and permissions.
- Third-party license inventory.
- Installer, upgrade path, internationalization coverage.

This roadmap is a plan, not a claim that all these features already work. The previous UEFI-only prototype has no compatibility runtime. The usable target is a Linux-based custom distribution, not a repackaged static desktop mockup.
