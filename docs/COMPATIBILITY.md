# Windows and Android in Aevonyr OS

## Windows executables
Wine translates Windows API calls to Linux-compatible calls. Aevonyr detects the installed wine executable and uses it to open supported EXE and MSI files. It does not reimplement the Windows API or claim ownership of Wine. Running arbitrary installers is a security risk, so user confirmation is required in the GUI.

## Android packages
Waydroid runs an Android image in a Linux container. It requires a Wayland session and suitable kernel features. Aevonyr passes selected APKs to Waydroid for installation. Installed apps can subsequently launch in Android; selecting an APK is not a direct Windows-style app execution. ARM-only apps may not run on x86-64 without additional compatibility work.

## Important limits
The current app does not install or initialize either runtime, guarantee that a program works, install Linux drivers, or boot as an ISO. Packaging an independent Aevonyr ISO is a future release task.

Upstream information: https://www.winehq.org/about/ and https://docs.waydro.id/
