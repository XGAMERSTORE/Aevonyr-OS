# Aevonyr OS 1.0 — Eclipse Edition 💜

**One System. Two Worlds.**

Aevonyr is an experimental Debian 13 Linux Live distribution with KDE Plasma, a branded control interface, Linux/Windows/Android application integration and local recovery tools.

## New in 1.0
- Aevonyr Pulse: actual CPU, RAM and storage utilization, uptime and a live historical graph (no fabricated data).
- Aevonyr Launcher and Universal App Hub: native Linux, Flatpak and Waydroid applications.
- Eclipse purple visuals, login screen, startup/shutdown animation and first-login setup.
- KDE Discover software/firmware updates, KDE Connect Phone Link, system diagnostics.
- Timeshift system snapshots and Back In Time personal-file backups.
- Fixed ISO verification that incorrectly failed the previous 0.9 build after successfully creating an ISO.
- BIOS and UEFI boot catalog, Linux squashfs and SHA256 image checks; experimental QEMU screenshot captures.

### Download
Open https://github.com/XGAMERSTORE/Aevonyr-OS/actions/workflows/build-linux-iso.yml and choose the most recent successful Linux ISO build. Download the artifact named aevonyr-os-1.0.0-eclipse-live-amd64, unpack it, and check SHA256SUMS against Aevonyr-OS-1.0.0-Eclipse-Live-amd64.iso.

### Applications and commands
- aevonyr — graphical control application
- aevonyr --pulse — real system resource dashboard
- aevonyr --launcher — fullscreen installed application search
- aevonyr --app-hub — combined application hub
- aevonyr --welcome — first-run wizard
- aevonyr --phone — KDE Connect
- aevonyr --updates — KDE Discover and fwupd integrations
- aevonyr --restore — Timeshift and Back In Time
- aevonyr --diagnose — local diagnostic report

### Build
On Debian 13 with root permission and internet, install live-build, debootstrap, squashfs-tools, xorriso, grub-efi-amd64-bin and grub-pc-bin. Run sudo ./iso/build.sh to create an ISO in dist/.

Run Python tests with python3 -m unittest discover -s tests -v.

### Status and safety
**1.0 Eclipse Edition is currently a Release Candidate, not a hardware-certified stable release.** A successful GitHub Actions build checks the image contents but does not prove correct graphical login, installation, hardware support or recovery. Test on a disposable VirtualBox machine using a blank virtual disk before installing on physical hardware. Wine/Waydroid compatibility varies. Aevonyr uses the KDE compositor rather than a proprietary new window system.

See docs/RELEASE-1.0.md, docs/VIRTUALBOX-TEST.md and docs/LINUX-LIVE-ISO.md for limitations and testing. Third-party software licenses and an Aevonyr project license must be addressed before broad public distribution.
