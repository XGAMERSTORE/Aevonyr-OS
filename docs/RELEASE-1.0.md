# Aevonyr OS 1.0 Eclipse Edition — Release Candidate

One System. Two Worlds.

## Shipped in the source tree
- Linux kernel and Debian 13, KDE Plasma Wayland, SDDM user login and genuine NetworkManager connectivity.
- Purple Eclipse colors, wallpaper, startup and shutdown theme, Czech and English Welcome guide.
- Aevonyr Pulse real CPU, memory, disk, uptime and live chart; KDE System Monitor access.
- Aevonyr Launcher and App Hub with installed native/Flatpak/Waydroid apps, supported Windows apps via Wine.
- Discover updates with firmware backend, KDE Connect phone pairing.
- Timeshift for installed-system snapshots and Back In Time for personal files. No silent restore or installation.
- Fixed xorriso verification: the -ls command lists the Linux live filesystem (the previous -find -print flag is unsupported).
- Added explicit checks for BIOS/UEFI El Torito, squashfs and ISO checksum; optional QEMU screenshots help debugging.

## Image
The target image is Aevonyr-OS-1.0.0-Eclipse-Live-amd64.iso. The matching GitHub Actions artifact is aevonyr-os-1.0.0-eclipse-live-amd64.

Download from https://github.com/XGAMERSTORE/Aevonyr-OS/actions/workflows/build-linux-iso.yml by choosing a successful run, and extract the ZIP. Verify the included SHA256SUMS.

## Acceptance checklist before stable 1.0
- Boot in BIOS and UEFI virtual machines and visually confirm KDE session and Aevonyr Welcome.
- Open Aevonyr Pulse and confirm CPU/memory graph values change over time.
- Confirm real network, Firefox, sounds, keyboard, graphics, password/login and shutdown.
- Test installer only on a fresh blank VM disk, verify reboot and created user account.
- Verify one trusted Wine EXE; Android needs Waydroid initialization and compatible hardware/kernel.
- Test an application install, firmware-update UI and safe recovery of disposable snapshots.
- Verify licenses, security updates, accessibility, translations and hardware compatibility.

### Important
Until these tests have been performed, the ISO is not a proven stable OS. QEMU screenshots verify only that a VM can display graphics; they do not prove successful login or safe disk installation.
