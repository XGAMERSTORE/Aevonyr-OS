// Bookish Applications layout. Run through the guarded per-user installer.
(function () {
    var old = panels();
    // Idempotent after interrupted invocations: never create duplicate panels.
    for (var i=0; i<old.length; ++i) {
        old[i].currentConfigGroup = ["Aevonyr"];
        if (old[i].readConfig("Orbit", "") === "v1") {
            print("AEVONYR_ALREADY_APPLIED"); return;
        }
    }
    var rail, status;
    try {
        rail = new Panel;
        rail.location = "left";
        rail.height = 68;
        rail.hiding = "none";
        var orbit = rail.addWidget("org.kde.plasma.icon");
        orbit.currentConfigGroup = ["General"];
        orbit.writeConfig("url", "file:///usr/share/applications/aevonyr-launcher.desktop");
        var tasks = rail.addWidget("org.kde.plasma.icontasks");
        tasks.currentConfigGroup = ["General"];
        tasks.writeConfig("launchers", ["applications:bookish-library.desktop", "applications:org.kde.dolphin.desktop", "applications:firefox-esr.desktop", "applications:aevonyr-os.desktop"]);
        rail.addWidget("org.kde.plasma.pager");
        rail.addWidget("org.kde.plasma.showdesktop");
        status = new Panel;
        status.location = "top";
        status.height = 32;
        status.addWidget("org.kde.plasma.panelspacer");
        var clock = status.addWidget("org.kde.plasma.digitalclock");
        clock.currentConfigGroup = ["Appearance"];
        clock.writeConfig("showDate", true);
        clock.writeConfig("use24hFormat", 2);
        status.addWidget("org.kde.plasma.panelspacer");
        status.addWidget("org.kde.plasma.systemtray");
        // Old panels stay until both replacements have been populated.
        if (rail.widgetIds.length < 4 || status.widgetIds.length < 4) {
            throw new Error("Orbit widgets missing");
        }
    } catch (e) {
        if (rail) rail.remove();
        if (status) status.remove();
        throw e;
    }
    for (var j=0; j<old.length; ++j) old[j].remove();
    rail.currentConfigGroup = ["Aevonyr"];
    rail.writeConfig("Orbit", "v1");
    status.currentConfigGroup = ["Aevonyr"];
    status.writeConfig("Orbit", "v1");
    print("AEVONYR_APPLIED");
})();
