# Aevonyr OS 💜

**One System. Two Worlds.**

Aevonyr OS is a custom Linux distribution project built on Debian 13, KDE Plasma/Wayland, Wine and optional Waydroid. It is an experimental PC operating system project, not a certified Windows/Android replacement or a finished commercial OS.

**Development status:** Version 0.8.0 adds a fullscreen application launcher, a Universal App Hub and separate System Restore and personal backup tools. GitHub Actions has built previous 0.7.x Linux ISO images successfully, but this 0.8 candidate requires its own full build and VirtualBox boot testing.

## Download and test the ISO

Open the [Linux ISO build workflow](https://github.com/XGAMERSTORE/Aevonyr-OS/actions/workflows/build-linux-iso.yml). Open the latest successful build, download the artifact ZIP and extract the ISO and SHA256SUMS. Verify its checksum before booting in a new empty VirtualBox VM.

Do not confuse the multi-gigabyte Linux Live ISO with the old 17 MB UEFI preview.

## Aevonyr 0.8 features

- Real Linux kernel and drivers, KDE Plasma desktop, SDDM login, NetworkManager and Firefox ESR.
- Branded Aevonyr Eclipse color scheme, wallpaper, login screen and boot/shutdown animation.
- **Aevonyr Launcher:** fullscreen search and launch for installed native Linux, Flatpak and Android apps. Uses KDE for window management.
- **Universal App Hub:** browse and launch installed Linux, Flatpak and Waydroid apps; install a user-approved Flatpak from a curated selection; enable Flathub explicitly when needed.
- Windows EXE/MSI opening through Wine, APK installation through Waydroid. Not all Windows/Android applications are compatible.
- **System Restore:** Timeshift GUI for system snapshots on installed Aevonyr systems and Back In Time for personal documents/photos/projects.
- File browser, notes, diagnostics, languages, network settings and KDE session actions.
- Calamares graphical installer; only test disk installation on a disposable virtual machine until validated.

## Useful commands

- aevonyr — Aevonyr desktop controls.
- aevonyr --launcher — fullscreen search. Escape closes it.
- aevonyr --app-hub — Universal App Hub.
- aevonyr --restore — system snapshots and user backups.
- aevonyr --diagnose — Linux runtime diagnostics.
- aevonyr --languages — available interface languages.

The three new apps also have entries in the KDE application menu.

## Safety

System snapshots and user backups are different things. Timeshift excludes personal user files by default. Aevonyr requires explicit user action before enabling Flathub, installing apps or opening restore tools, and prevents launching system restore from the temporary Live environment. No disk is automatically formatted or restored.

Our KDE app/launcher does **not** replace the Plasma compositor. The build pipeline validates the generated ISO structure, but actual boot, login, disk-installation safety, graphics and compatibility still need testing.

See [the App Hub and Restore guide](docs/APP-HUB-RESTORE.md), [Linux ISO builder](docs/LINUX-LIVE-ISO.md), [VirtualBox test guide](docs/VIRTUALBOX-TEST.md) and [roadmap](docs/ROADMAP.md).

## Build

On Debian 13 with enough disk space, internet and root permission, install live-build, debootstrap, squashfs-tools, xorriso, grub-efi-amd64-bin and grub-pc-bin. Then run:

    sudo ./iso/build.sh

Output target: dist/Aevonyr-OS-0.8.0-Linux-Live-amd64.iso and dist/SHA256SUMS.

Python tests:

    python3 -m unittest discover -s tests -v
    python3 -m compileall -q aevonyr

Third-party software retains its respective upstream licensing and distribution obligations. An Aevonyr project license is still to be decided before general release.
