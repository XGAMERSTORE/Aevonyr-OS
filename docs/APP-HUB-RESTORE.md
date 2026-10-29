# Universal App Hub and System Restore — Aevonyr 0.8.0

## The Aevonyr app launcher

Select Aevonyr Launcher in the KDE application menu, or run aevonyr --launcher. It opens a fullscreen searchable launcher and gathers:
- Linux applications from standard XDG .desktop files.
- Flatpak applications from the installed Flatpak list.
- Android applications from Waydroid when the runtime is accessible.

Double-click an app or press Enter to launch it. Press Escape to close. It is a branded app launcher within KDE, not a standalone display compositor or a replacement for the KDE panel.

## Installing applications

Open Aevonyr App Hub in the KDE application menu or run aevonyr --app-hub.

Installed Linux applications are opened using GIO desktop-file handling. Flatpak applications run using the Flatpak runtime. Installed Android apps are launched through Waydroid. Choose EXE/MSI or Install APK to use Wine and Waydroid respectively.

The featured Flatpak suggestions are a fixed starter list rather than an online catalog. Press Enable Flathub if you want to add the remote for your Linux user. This action needs confirmation. Press Install selected to open Konsole with Flatpak's interactive installer, which lets you review permissions before proceeding. Aevonyr does not use noninteractive yes-to-all flags.

KDE Discover is another full graphical option for searching and updating supported apps. Aevonyr includes the Discover Flatpak backend.

Flatpak reference: https://docs.flatpak.org/en/latest/using-flatpak.html

## Restore Center: two distinct responsibilities

Open Aevonyr System Restore or run aevonyr --restore.

**Timeshift:** A system snapshot/restore utility for installed Linux systems. It protects system files and settings; by default it excludes personal data. Configure it on a suitable installed filesystem with adequate free space. For its Btrfs mode, Timeshift expects a supported root/subvolume layout; do not assume all default Calamares layouts qualify.

**Back In Time:** A separate tool for backups of your personal files and folders. Choose the folders and ideally a separate disk for backups, then perform a test restore of a disposable document.

The Aevonyr UI blocks system snapshots from the temporary Live environment. It never automatically starts a snapshot or restore operation; it opens upstream graphical tools with explicit user confirmation. This is not a transactional OS rollback solution.

Timeshift: https://github.com/linuxmint/timeshift
Back In Time: https://github.com/bit-team/backintime

## VirtualBox validation checklist

1. Finish the GitHub Actions ISO build and check its SHA256SUMS.
2. Boot with EFI on a blank 40+ GB virtual disk, and test the default KDE session.
3. Open Aevonyr Launcher; verify typing, Enter, Escape and launching a known native app.
4. Check the App Hub lists installed apps. Optionally enable Flathub and test a small trusted application.
5. In Live mode, verify that system snapshot management refuses to start.
6. Install onto the blank VM disk and reboot from that virtual disk.
7. Configure Timeshift. Create and verify a snapshot, then test recovery only on disposable test data.
8. Configure Back In Time separately, ideally to an external virtual disk. Perform a test-file recovery.
9. Test EXE/MSI/Android APK compatibility separately. Waydroid requires initialization, kernel support and Wayland.

Until these steps pass, do not install on a real disk containing valuable data.
