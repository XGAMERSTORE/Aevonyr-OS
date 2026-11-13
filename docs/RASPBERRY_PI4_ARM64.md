# Raspberry Pi 4 (8 GB) — ARM64 research target

**Status: ARM64 userspace build only. NOT a bootable Raspberry Pi OS image.**

The Raspberry Pi 4 (8 GB) is an intended Bookish OS target. The initial CI
pipeline builds a Debian Bookworm ARM64 container containing the existing
Python/Tk Bookish shell, then checks its architecture, Python compilation and
headless CLI with QEMU user-mode emulation.

The image is **not** an SD card image, ISO, kernel, firmware, UEFI, desktop
session or proof of physical Raspberry Pi boot. Tk GUI is not tested here.
Waydroid, Wine, GPU acceleration, Wi-Fi, audio, touchscreen and USB hardware
are not validated. Do not flash this container to an SD card.

To reproduce on a host with Docker Buildx and QEMU/binfmt:
```sh
docker buildx build --platform linux/arm64 --load -f Dockerfile.arm64 -t bookish-arm64:local .
docker run --rm --platform linux/arm64 bookish-arm64:local python3 -m bookish --languages
```

Next hardware milestone: start from a supported Raspberry Pi OS 64-bit
installation, verify a graphical Tk session and Bookish shell on a real Pi 4,
then design a reproducible Pi-specific SD image with documented firmware,
kernel, boot partition, checksums and recovery procedure. This is separate
from experimental Realme Pad MT6768 bootchain research.
