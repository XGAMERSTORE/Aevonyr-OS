# Aevonyr OS Linux Live 0.7

Unlike the 0.6 UEFI demo, this is a **Debian 13 based real Linux Live OS build recipe**.

## Software components
- Debian 13 Trixie, x86-64 kernel, live-boot and live-config.
- KDE Plasma Wayland, SDDM login; NetworkManager provides real Wi-Fi/Ethernet with hardware drivers.
- Firefox ESR, Dolphin file manager, Kate text editor, package updater and audio tools.
- Wine / Wine64 are included to run supported EXE/MSI programs.
- Waydroid is included from Trixie backports, but the separate Android image must be downloaded and initialized before APK apps will work. A Wayland session and kernel binder support are required. Use the "Set up Android apps" launcher. ARM-only apps may not work on x86 PCs.
- Calamares installer: back up your disk; ONLY test installations in a blank VM disk before attempting physical hardware.
- English-first Aevonyr shell with language packs; full system and KDE translations are separate.

## Build
Use Debian 13 (with root permissions, internet and at least 20 GiB of free disk space):
```bash
apt-get update
apt-get install -y live-build debootstrap squashfs-tools xorriso grub-efi-amd64-bin grub-pc-bin
sudo ./iso/build.sh
```
Output: `dist/Aevonyr-OS-0.7-Linux-Live-amd64.iso` and `dist/SHA256SUMS`.
GitHub Actions also contains a build workflow that runs Debian in a privileged container and uploads the image if successful.

## Account/password and install
Live sessions may log in automatically under Debian's default live user. Normal account creation, password protection and optional full-disk encryption are managed by Calamares during installation. There is NO hard-coded login password in the Linux ISO, unlike the former UEFI demonstration. In live mode, changes normally do not survive reboot.

## Status and test checklist
This is **a build configuration, not a proven release** until all steps pass:
- [ ] Build ISO successfully with Debian packages and backports enabled.
- [ ] Boot on UEFI x86-64 VirtualBox/QEMU and check KDE, Aevonyr, mouse, keyboard, sound and internet.
- [ ] Launch one known-compatible EXE in Wine.
- [ ] Initialize Waydroid, start Android and install/open an x86 compatible APK.
- [ ] Test Calamares safely on an empty virtual disk; verify reboot and real user login.
- [ ] Test physical hardware, Wi-Fi firmware, BIOS compatibility, updates and security.
- [ ] Inventory redistribution notices for Debian, Wine, Waydroid, KDE and all bundled dependencies.

No technology can guarantee compatibility with every Windows/Android application. External upstream licenses continue to apply. Boot/shutdown graphics in the older UEFI demo are not reused as real Linux boot animation.

## 0.7.1 desktop experience
- Animated violet Aevonyr SDDM sign-in using actual system accounts and passwords.
- First-login Aevonyr wallpaper (later changes to the wallpaper are respected).
- Real NetworkManager connectivity page and native Wi-Fi/Ethernet connection editor; no secrets stored by the custom shell.
- KDE Breeze Plymouth graphical boot splash and `quiet splash` boot options; original Aevonyr boot animation is a future milestone.
- New regression tests. A built ISO is **not yet proof of VirtualBox boot, SDDM theme operation or app compatibility**.
