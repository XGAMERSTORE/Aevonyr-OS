# Bookish OS — a cozy home for readers

**A little home for big stories — for Niki.**

Bookish OS (formerly Bookish OS) is an experimental Debian 13 Linux Live distribution with KDE Plasma, a branded control interface, Linux/Windows/Android application integration and local recovery tools.

## Bookish library
- Local EPUB/PDF/TXT bookshelf, manually recorded reading percentage and notes: `bookish --books`.
- Calibre for reading and organizing books; Okular for PDFs; LibreOffice Writer and FocusWriter for writing.
- Opt-in TXT translation through a user-configured HTTPS LibreTranslate service. Languages come from that service; an API key may be required. No service or key is bundled. Books are sent only after confirmation. Literary quality and every language are **not** guaranteed. Export EPUB text with Calibre first; DRM-protected books are not bypassed.
- Original files stay unchanged. Keep removable book media connected. Live sessions without persistence lose library notes on reboot.
- Internal `aevonyr` command, file paths and Python package remain as compatibility identifiers. The public name is Bookish OS. Repository URL is unchanged pending repository administration access.

## New in 1.0
- Bookish Pulse: actual CPU, RAM and storage utilization, uptime and a live historical graph (no fabricated data).
- Bookish Launcher and Universal App Hub: native Linux, Flatpak and Waydroid applications.
- Paper-and-sage desktop, bookshelf wallpaper, branded login and startup screen.
- KDE Discover software/firmware updates, KDE Connect Phone Link, system diagnostics.
- Timeshift system snapshots and Back In Time personal-file backups.
- Fixed ISO verification that incorrectly failed the previous 0.9 build after successfully creating an ISO.
- BIOS and UEFI boot catalog, Linux squashfs and SHA256 image checks; experimental QEMU screenshot captures.

### Download
Open https://github.com/XGAMERSTORE/Aevonyr-OS/actions/workflows/build-linux-iso.yml and choose the most recent successful Linux ISO build. Download the artifact named bookish-os-1.0.0-live-amd64, unpack it, and check SHA256SUMS against Bookish-OS-1.0.0-Live-amd64.iso.

### Applications and commands
- aevonyr — graphical control application
- aevonyr --pulse — real system resource dashboard
- aevonyr --launcher — compact Orbit application search
- aevonyr --open FILE — graphical EXE/MSI/APK/DEB opening (also the default file handler)
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
**Bookish 1.0 is currently a Release Candidate, not a hardware-certified stable release.** A successful GitHub Actions build checks the image contents but does not prove correct graphical login, installation, hardware support or recovery. Test on a disposable VirtualBox machine using a blank virtual disk before installing on physical hardware. Wine/Waydroid compatibility varies. Bookish uses the KDE compositor rather than a proprietary new window system.

See docs/RELEASE-1.0.md, docs/VIRTUALBOX-TEST.md and docs/LINUX-LIVE-ISO.md for limitations and testing. Third-party software licenses and an Bookish project license must be addressed before broad public distribution.

## Orbit desktop preview

The Orbit review branch adds a new application overview, left task rail, top status
bar and original paper/sage bookshelf artwork. See [Orbit setup, rollback and test limits](docs/ORBIT-DESKTOP.md).
It remains a Debian/KDE-based experimental distribution. Previously built ISOs do not include this redesign.
