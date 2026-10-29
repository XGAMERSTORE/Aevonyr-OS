# Aevonyr OS 0.9 — Project Eclipse

Project Eclipse prioritizes useful everyday features, not decorative mock buttons. It is an experimental release candidate built on Debian 13 and KDE Plasma.

## First login

The Aevonyr Welcome window appears on the first login if it has not been completed. On a small screen, navigate using the Next/Back buttons and scroll the main Aevonyr sidebar when necessary.

Steps:
1. **Language:** English and Czech in the Aevonyr application. KDE desktop and app translations are separate and may require OS locale configuration.
2. **Network:** opens actual NetworkManager settings; Wi-Fi credentials are handled by Linux, not the wizard.
3. **Applications:** opens KDE Discover. Flatpak/Flathub installs require explicit approval.
4. **Phone:** KDE Connect pairing on your local network. Both devices must support the protocol; firewall/network segmentation may block discovery.
5. **Backup:** opens Back In Time to configure user-file backups. Prefer a separate external storage destination.
6. **Finish:** marks the welcome process complete. Closing or skipping it without Finish leaves it available on next login.

To restart onboarding manually: `aevonyr --welcome`.

Completion writes only `~/.config/aevonyr-os/welcome-state.json` with the boolean `completed`. No account credentials, device IDs or network secrets are saved by this feature.

## System and firmware updates

Run `aevonyr --updates` or select **Aevonyr Updates**.

This opens KDE Discover for application and distribution updates. The project now includes PackageKit and Flatpak integration, plus the fwupd backend for firmware supported by the machine. Firmware updates can require a reboot and may not be offered in VirtualBox. Review every change and keep a good backup before an update.

The Aevonyr UI itself **does not** silently execute apt upgrade or flash firmware. It opens established system tools.

## Phone Link

Run `aevonyr --phone` to open the integration pane. Pairing opens KDE Connect's settings UI; your phone must have the companion KDE Connect application. The app may show a count of **paired and currently reachable** devices, not a list of device IDs. Aevonyr does not silently pair with or send data to phones.

## Still to test before production use

- UEFI/BIOS ISO boot and installer on a blank virtual disk.
- SDDM login, Wayland desktop, first-run wizard, scrolling/navigation on small screens.
- Wi-Fi, firmware backend availability, Flatpak and Discover update handling.
- KDE Connect discovery and pairing with a supported phone on a local network.
- Timeshift and Back In Time real restore tests on disposable data.
- Hardware drivers, security updates and upgrade path.

GitHub Actions checks Python tests, image checksums, El Torito boot information and squashfs presence. This is **not an automated graphical boot test**. VirtualBox or QEMU boot validation remains required.

Relevant upstream projects: KDE Discover, NetworkManager, KDE Connect, fwupd and Debian live-build.
