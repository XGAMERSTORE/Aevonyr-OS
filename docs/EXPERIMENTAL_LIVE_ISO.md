# Experimental Bookish OS Live ISO (x86_64)

This is an **experimental Debian Bookworm live image** with XFCE as its underlying desktop and the Bookish Python/Tk application launched at login. It is **not** a standalone compositor, polished installer, or an ARM64 tablet image.

## Build in Linux

Install `live-build` and `rsync`, then from the repository root:

```sh
sudo bash scripts/build-live-iso.sh
```

The script creates `build/bookish-live/*.iso` and a SHA-256 file **only if the build succeeds**. It requires network access to Debian repositories and substantial disk space. Run only in a disposable build environment; the output directory is build state, not a source tree.

Alternatively, use GitHub Actions → **Bookish OS x86_64 live ISO (experimental)** → **Run workflow**. Only a successful run with a published `bookish-os-x86_64-live-experimental` artifact proves that an ISO file was produced.

## Virtual machine smoke test

Use a new, empty VirtualBox VM: Linux / Debian 64-bit, at least 4 GB RAM, 2 CPU cores and 20 GB disposable virtual disk. Attach the ISO as optical media and boot in live mode. Confirm that XFCE starts and that the Bookish window opens. Test notes and file browsing, reboot and shut down. Do **not** assume persistence, an installer, working Wine/Waydroid, or tablet support.

## Explicit limitations

- This is a Debian-based prototype with Bookish branding, not a completed independently maintained distribution.
- There is no validated hardware compatibility, boot test or installation test until separately performed.
- No Realme Pad RMP2102/RMP2103 support or bootloader modifications are included.
- Do not distribute as a finished release until boot, security, packaging and license review pass.
