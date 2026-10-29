# Test Aevonyr OS 0.7.2 safely in VirtualBox

## 1. Download and verify
- Open the latest successful [GitHub Actions ISO build](https://github.com/XGAMERSTORE/Aevonyr-OS/actions/workflows/build-linux-iso.yml).
- Download and extract the artifact ZIP; select the **.iso file**, not the ZIP.
- Verify it matches the published SHA256SUMS. On Windows: `certutil -hashfile Aevonyr-OS-0.7.2-Linux-Live-amd64.iso SHA256`.

## 2. Create a disposable VM
Use VirtualBox 7.x, **Linux / Debian (64-bit)**, 4 GB RAM or more (6 GB recommended for Waydroid), 2–4 virtual CPUs, VMSVGA graphics, ~128 MB video RAM, a **new blank 40+ GB virtual disk**, EFI enabled and Secure Boot off. Connect the ISO as an optical drive and keep NAT network mode enabled.

Do **not** mount your physical disk as a raw disk. Do **not** test Calamares on a disk containing real data.

## 3. First boot
- Start the VM and choose the Live boot option.
- KDE Plasma and the Aevonyr application should load after the SDDM/live session starts.
- The Plymouth splash and animated login theme are under test; take a screenshot if either fails.
- Check network status in Aevonyr's **Network** pane and open Firefox.

## 4. Collect support information
Open Konsole and run:
```bash
aevonyr --diagnose
ip link
uname -a
```
Share non-sensitive output and VM screenshots when reporting a problem. Do not share passwords or private network details.

## 5. App checks
- Check Wine with `wine --version`. Use a small trusted Windows EXE for a compatibility test.
- Check Waydroid with `waydroid status`. Setup requires initialized Android images, kernel binder support and a functional Wayland session; a headless VirtualBox VM may be incompatible.
- Never run an untrusted EXE/APK merely to test the launcher.

## 6. Installer check
Use **Install Aevonyr OS** only with the VM's **blank virtual disk**, and review Calamares partition choices carefully. Reboot from that virtual disk after installation and confirm the new account/password. Backups remain essential even after a successful VM test.

## Current confidence
The CI pipeline checks the source code, generates the ISO, validates its existence and its SHA256 checksum. It does **not yet automatically confirm** graphical boot, SDDM theme loading, hardware support or the Calamares installation. Those need a manual VirtualBox run or dedicated VM smoke tests.
