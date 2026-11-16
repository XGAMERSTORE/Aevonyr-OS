# Bookish OS — Raspberry Pi 4 (8 GB), ARM64

## What is built

The `Bookish OS Raspberry Pi 4 ARM64 image` GitHub Actions workflow builds an
experimental SD-card `.img.xz` using Raspberry Pi's official `pi-gen` ARM64
pipeline, pinned in `pi/pi-gen-revision`. It uses Raspberry Pi OS Trixie,
its Pi firmware/kernel, boot partition, desktop, graphics and network packages,
then adds the current Bookish Python/Tk shell, Calibre, LibreOffice Writer and
FocusWriter. This is separate from the x86 live ISO and Realme Pad research.

**Build success is not hardware validation.** Until a real Pi 4 boot has been
recorded, the image remains experimental. The existing ARM64 Docker workflow
only tests userspace and cannot produce an SD-card image.

## Get and start an image

1. Open Actions → **Bookish OS Raspberry Pi 4 ARM64 image**. Select a successful
   run for the desired commit and download the `bookish-pi4-arm64-<commit>` artifact.
   A failed or running workflow does not imply a usable image exists.
2. Extract the artifact ZIP. Verify `sha256sum -c SHA256SUMS` in that directory.
3. In Raspberry Pi Imager choose Raspberry Pi 4, **Use custom** and the `.img.xz`.
   Select a spare microSD card (32 GB recommended). Writing erases that selected
   card. Keep the current working card as a recovery option.
4. Connect display, keyboard and mouse, then boot the Pi. Complete Raspberry Pi
   OS first-boot account setup. There is no shared default password; SSH is off.
   Czech keyboard/locale, Europe/Prague and Czech Wi-Fi regulatory region are
   defaults; change them if needed.
5. Bookish starts inside the Pi desktop after login. It can also be started from
   the applications menu or with `bookish-session`. Closing Bookish returns to
   the underlying desktop. Reading tools are available from that desktop menu.

## Build locally

Use a native ARM64 Debian/Ubuntu host with root access, loop devices and ample
free space (at least 30 GB recommended). The workflow lists build dependencies.
From a fresh checkout:

```sh
sudo bash scripts/build-pi4-image.sh /absolute/new-build-directory
```

The directory must not already exist. Outputs are under `pi-gen/deploy` within
it: compressed image, `SHA256SUMS`, build provenance and this guide. The builder
writes image files, never a physical SD card. The pi-gen source revision is
pinned; apt repositories are not snapshots, so builds are not byte reproducible.

## Compatibility and acceptance checklist

| Area | Evidence / remaining validation |
| --- | --- |
| ARM64 Python and CLI | Existing container CI passed; new image CI runs native ARM64 tests |
| Tk desktop | New CI creates the actual application under Xvfb; physical display pending |
| Pi boot/kernel/firmware | Supplied by official pi-gen; physical Pi 4 boot pending |
| 8 GB RAM | 64-bit target; verify available RAM with `free -h` on the device |
| HDMI, graphics, audio | Raspberry Pi OS drivers; hardware tests pending |
| Ethernet, Wi-Fi, Bluetooth, USB | Raspberry Pi OS packages; hardware tests pending |
| EPUB/PDF/office documents | Calibre and Writer included; open sample documents on hardware |
| Windows games / EXE | No x86 translation or Wine supplied; not claimed compatible |
| Android / APK | Waydroid not supplied or validated |

On a real Pi 4, record `uname -a`, `dpkg --print-architecture`, `free -h`,
`cat /proc/device-tree/model`, first login, Bookish launch, HDMI resolution,
network connectivity, sound, USB, and a reboot. `dpkg` must report `arm64`.
The version under `/opt/bookish/build-info.txt` identifies the exact sources.
