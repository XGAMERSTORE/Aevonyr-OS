# Aevonyr OS Architecture

Brand: Aevonyr OS — One System. Two Worlds.
Current stage: Python/Tk desktop shell on existing Linux, not yet bootable ISO.

Target layers:
1. Linux kernel, bootloader, drivers, filesystems and security updates.
2. Wayland desktop/compositor, window management and Aevonyr UI.
3. Wine compatibility runtime for supported Windows EXE/MSI, installed and licensed from upstream.
4. Waydroid container with initialized Android image, Wayland session and binder kernel support for APKs.
5. Internationalization via validated language packs, regional formatting, accessible fonts and input methods.
6. Reproducible bootable ISO build, installer, tests, signed updates and license notices.

Current Wine/Waydroid code only forwards files to locally installed runtimes. It does not include Wine, Waydroid or Android and cannot boot by itself.
Android APK installation is not equivalent to immediate app launch. Windows/Android compatibility varies by program and CPU architecture.

Bootable ISO acceptance: QEMU/VirtualBox and physical hardware tests; functional storage, networking and display; EXE runtime and APK install/launch tests; installation and update checks.

Upstream:
https://www.winehq.org/about/
https://docs.waydro.id/
https://www.gnu.org/software/gettext/manual/gettext.html
