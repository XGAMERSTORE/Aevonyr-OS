# Aevonyr OS 💜

**One System. Two Worlds.**

Aevonyr OS is a custom **Linux-based PC operating system project**. The current Linux Live candidate is built with Debian 13 (Trixie), KDE Plasma 6, Wayland, NetworkManager, Wine and optional Waydroid. It runs a custom Aevonyr desktop/control application and includes an installer.

> **Status:** Experimental. The 0.7.1 ISO built successfully in GitHub Actions. The improved 0.7.2 build includes the Aevonyr Eclipse boot/shutdown animation, health diagnostics and session controls. The build pipeline is not a substitute for actual VirtualBox and physical hardware testing. Do **not** install it to a valuable disk without a tested backup.

## Download an actual Linux Live ISO

1. Open [Aevonyr Linux ISO GitHub Actions](https://github.com/XGAMERSTORE/Aevonyr-OS/actions/workflows/build-linux-iso.yml).
2. Choose the latest successful **Build Aevonyr Linux Live ISO** run.
3. In **Artifacts**, download `aevonyr-os-0.7.2-linux-live-amd64` (or the previous 0.7.1 build artifact).
4. Extract the ZIP to obtain the real .iso file and SHA256SUMS.
5. Verify the SHA256 checksum before use. See [VirtualBox testing guide](docs/VIRTUALBOX-TEST.md).

This is a multi-gigabyte Linux image, **not** the 17 MB older standalone UEFI UI preview.

## Linux Live features

- Bootable x86-64 Debian Linux system, Linux kernel and real hardware drivers.
- KDE Plasma desktop with Wayland and Aevonyr-specific violet branding.
- Aevonyr Eclipse Plymouth startup/shutdown animation (0.7.2 candidate).
- SDDM graphical sign-in using **actual Linux system accounts**. There is no shared demo password in this Linux edition.
- NetworkManager handles actual Wi-Fi/Ethernet, credentials and connectivity. Firefox ESR is bundled.
- Wine and Wine64 for **supported** Windows EXE/MSI programs (not every app/game is compatible).
- Waydroid for supported Android APKs, requiring initialization, an Android image download, suitable kernel support and Wayland. Some ARM apps are unsupported.
- English-first Aevonyr control app with importable translation packs and built-in starter languages.
- Diagnostics: Linux, internet connection, Wine, Waydroid, disk space; copy a support report.
- Power and session: lock screen, log out, restart and shut down (with confirmation).
- Calamares graphical installer with a separate warning before disk operations.

## Using Aevonyr on Linux

Open the **Aevonyr OS** application menu entry, or run:

```bash
aevonyr
aevonyr --diagnose
aevonyr --check
aevonyr --languages
```

Use **Network** for connectivity and **System Health** for diagnostics. Open **Set up Android apps** to initialize Waydroid if you are in a working Wayland session; initialization downloads additional images.

## Building from source

Use Debian 13 with root access and significant free disk space (~20 GiB minimum, more recommended). See [Linux ISO build instructions](docs/LINUX-LIVE-ISO.md):

```bash
apt-get update
apt-get install -y live-build debootstrap squashfs-tools xorriso grub-efi-amd64-bin grub-pc-bin
sudo ./iso/build.sh
```

Built image: `dist/Aevonyr-OS-0.7.2-Linux-Live-amd64.iso`, with checksum `dist/SHA256SUMS`.

Run tests:

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q aevonyr
```

## Architecture and limits

Aevonyr's own graphical shell is currently a **Python/Tk app within KDE**, not a wholly new display server/window compositor. Wine and Waydroid are third-party upstream projects included according to distribution packaging. The final hardware/driver support and actual installer behavior are still being validated. See [roadmap](docs/ROADMAP.md), [compatibility notes](docs/COMPATIBILITY.md), and [translation guide](docs/TRANSLATING.md).

Original Aevonyr sources still need a project license decision before wide public distribution. Debian/KDE/Wine/Waydroid software retain their upstream licenses and obligations.
