# Aevonyr OS 1.0 — safe VirtualBox testing

Download Aevonyr-OS-1.0.0-Eclipse-Live-amd64.iso from a successful GitHub Actions artifact; extract it from ZIP and compare with SHA256SUMS.

Create an empty VirtualBox 7.x VM: Debian 64-bit, EFI enabled, Secure Boot off, VMSVGA, 128 MB video RAM, 4–6 GB RAM, 2 or more CPUs, at least 40 GB of NEW VIRTUAL disk, NAT network.

Boot the ISO. Verify:
1. BIOS or UEFI boot screen and SDDM/KDE session
2. Aevonyr Welcome, network connection, browser and KDE Discover
3. Aevonyr Pulse: CPU and RAM meters plus changing history graph
4. Launcher, App Hub, Phone Link, notes, backup and restore views
5. Login/logout, reboot and shutdown

Only test Calamares on the VM's disposable disk; never point it to a drive containing personal data.

In Konsole, run: aevonyr --diagnose, wine --version, waydroid status. Waydroid may not work in VirtualBox without supported Wayland/kernel binder features.

A screenshot smoke from QEMU is diagnostic only, not proof of complete OS boot/login or installer safety. Do not install to your main computer before actual test results and backups.
