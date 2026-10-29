# Aevonyr OS 💜

**One System. Two Worlds.**

Aevonyr OS is an experimental **Debian 13-based Linux Live distribution** with KDE Plasma, Wayland, a custom Aevonyr interface, Wine and optional Waydroid. It is not a new kernel or a Windows/Android replacement.

## Aevonyr 0.9 — Project Eclipse

This experimental development release adds:
- **Aevonyr Welcome:** first-login graphical wizard in Czech and English. Covers language, internet, application store, KDE Connect phone pairing and backups. Finishing writes a minimal local completion flag so the wizard doesn't repeatedly appear.
- **Aevonyr Updates:** opens KDE Discover to review Linux/Flatpak updates and eligible device firmware through fwupd. Nothing is installed without the user's approval.
- **Aevonyr Phone Link:** uses KDE Connect for local device pairing. Shows count of connected paired devices without storing device IDs.
- **Better navigation:** scrollable left navigation, quick links and Live mode warnings.
- **Branded Eclipse desktop:** existing Aevonyr color scheme, wallpaper, animated SDDM login and Plymouth splash.
- Previous 0.8 features: Universal App Hub, fullscreen launcher, Timeshift System Restore and Back In Time personal backups.

**Important limits:** Aevonyr still uses KDE Plasma as its compositor. Android requires Waydroid initialization, supported Linux kernel features and Wayland. Wine doesn't run every Windows application. Timeshift snapshots are not a substitute for external backups. ISO assembly does not prove graphical boot or installer safety.

## ISO downloads

Open [GitHub Actions — Aevonyr Linux ISO](https://github.com/XGAMERSTORE/Aevonyr-OS/actions/workflows/build-linux-iso.yml), select the most recent **successful** run and download its Artifact ZIP. The target for Project Eclipse is **Aevonyr-OS-0.9.0-Linux-Live-amd64.iso**; use a previous successful 0.8 image if the 0.9 build isn't green.

Unzip, verify SHA256SUMS, and test in a fresh empty VirtualBox VM first. Never select a physical disk containing important data.

See [safe VM testing](docs/VIRTUALBOX-TEST.md).

## Using the desktop

Commands:
- `aevonyr` — main app.
- `aevonyr --welcome` — first-run guide (can be reopened).
- `aevonyr --updates` — software and firmware management.
- `aevonyr --phone` — KDE Connect.
- `aevonyr --launcher` — fullscreen application search.
- `aevonyr --app-hub` — native/Flatpak/Android app hub.
- `aevonyr --restore` — Timeshift/Back In Time tools.
- `aevonyr --diagnose` — local system diagnostics.

KDE itself provides the real Wi-Fi/Ethernet, files, power, package management and system settings. The Aevonyr application provides a branded entry point rather than replacing those services.

## Building

On Debian 13 with root permission, internet and plenty of disk space:

```sh
apt-get update
apt-get install -y live-build debootstrap squashfs-tools xorriso grub-efi-amd64-bin grub-pc-bin
sudo ./iso/build.sh
```

The build generates `dist/Aevonyr-OS-0.9.0-Linux-Live-amd64.iso` plus SHA256SUMS.

Run source tests locally with `python3 -m unittest discover -s tests -v` and `python3 -m compileall -q aevonyr`.

See [Eclipse feature guide](docs/PROJECT-ECLIPSE.md), [build notes](docs/LINUX-LIVE-ISO.md), [compatibility roadmap](docs/ROADMAP.md) and [VirtualBox instructions](docs/VIRTUALBOX-TEST.md).

Third-party projects retain their own licenses. Before a public stable release, Aevonyr also needs a clearly documented project license, security/update policy and complete installation and hardware testing.
