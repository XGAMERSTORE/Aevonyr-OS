# Aevonyr Orbit — experimental desktop redesign

Orbit introduces an asymmetric application overview with ranked, multiword search,
keyboard selection, launch actions, original vector artwork and a graphite/lime palette.
A left application rail and separate top status panel replace the default bottom panel.
Running-window switching, network/audio status and workspaces remain native Plasma widgets.
Orbit is not a new kernel, compositor, or independently implemented window manager.

## New ISO / new account

The skeleton account contains a first-login token. After Plasma creates its default
panels, the per-user installer backs up the panel configuration, creates both new
panels, removes old panels only after population succeeds and records completion.
Subsequent logins preserve customization. Orbit opens once after initial layout setup.
The rail's Orbit icon reopens the application overview. Escape returns to the desktop.
Alt+F2 remains a native emergency route to launch `aevonyr --launcher` or Konsole.
Existing users without the token are not migrated automatically.

## Existing account (after installing these files)

Run `aevonyr-orbit-layout apply` inside the user's KDE session, without sudo.
This replaces panel layout; it backs up the previous config in
`~/.local/state/aevonyr/pre-orbit-appletsrc` (or XDG_STATE_HOME).
To return to the previous panels run `aevonyr-orbit-layout restore`.
Restore stops and starts the user's plasma-plasmashell systemd service and preserves
applications managed by KWin. If the service cannot stop, restore refuses to overwrite
its live configuration. The wallpaper and color scheme are independently adjustable
in System Settings; panel restore does not restore these.

## Acceptance checks

1. Boot a new ISO in a blank VM; confirm rail and top status panel, no duplicate bottom panel.
2. Orbit icon opens overview; type an installed app name, use arrows and Enter to launch.
3. Verify Escape, Tab focus, missing-app message, zero-result search, and mouse launch.
4. Test at 1024x768 and 1440x900; real Wayland/SDDM and multiple monitors need manual checks.
5. Open two apps; switch through rail and Alt+Tab. Check tray network/audio controls.
6. Log out/in: panels must not duplicate, and user customizations must remain.
7. Restore panels, log out/in, confirm automatic setup does not reapply.
8. Verify the live installer separately on a disposable virtual disk.

Python/Xvfb tests validate app behavior and screenshots only. They do not validate
Plasma's D-Bus scripting, panel rendering, hardware or installation. Use the CI run's
exact commit and SHA256SUMS; the older 1.0 ISO has none of these Orbit changes.

## Distribution and attribution

Aevonyr remains based on Debian GNU/Linux, KDE Plasma, KWin and other upstream packages.
Keep package copyrights, licenses, source obligations and upstream attribution intact.
The About dialog explicitly identifies this foundation. Do not market this as a new
kernel or guarantee that nobody will recognize Linux. Before public distribution,
review project licensing, bundled artwork and all third-party distribution obligations.
No release-stability claim is made by this design change.
