import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock
from aevonyr.apphub import (
    APP_ID, App, AppHubError, FEATURED, native_apps, flatpak_apps, android_apps,
    launch_command, enable_flathub_command, install_flatpak_command,
    installed_apps, valid_app_id, start,
)
from aevonyr.restore import RestoreError, is_live_boot, restore_command, backup_command


class AppHubTests(unittest.TestCase):
    @staticmethod
    def which(name):
        return "/usr/bin/" + name

    def test_application_ids(self):
        for appid in ("org.gimp.GIMP", "org.kde.krita", "com.valvesoftware.Steam"):
            self.assertTrue(valid_app_id(appid))
        for appid in ("", "../evil", "bad;touch /tmp/x", "org.gimp.GIMP --delete", "no.dots", "x"*201):
            self.assertFalse(valid_app_id(appid))
        self.assertGreaterEqual(len(FEATURED), 4)

    def test_native_desktop_files_and_hidden_override(self):
        with tempfile.TemporaryDirectory() as work:
            base=Path(work)
            user=base/"user"
            system=base/"system"
            user.mkdir();system.mkdir()
            (system/"browser.desktop").write_text("[Desktop Entry]\nType=Application\nName=Browser\nExec=firefox\n")
            (system/"hidden.desktop").write_text("[Desktop Entry]\nName=Secret\nNoDisplay=true\n")
            (user/"browser.desktop").write_text("[Desktop Entry]\nHidden=true\n")
            (user/"editor.desktop").write_text("[Desktop Entry]\nName=Editor\nExec=kate\n")
            apps=native_apps([user,system])
            self.assertEqual([a.name for a in apps],["Editor"])
            self.assertEqual(apps[0].source,"Linux")
            self.assertEqual(launch_command(apps[0],which=self.which),
                             ("/usr/bin/gio","launch",str(user/"editor.desktop")))

    def test_flatpak_list_and_run(self):
        fake=Mock(returncode=0,stdout="org.gimp.GIMP\tGIMP\ncom.valvesoftware.Steam\tSteam\nbroken\tBAD\n")
        run=Mock(return_value=fake)
        apps=flatpak_apps(which=self.which,run=run)
        self.assertEqual([a.identifier for a in apps],["org.gimp.GIMP","com.valvesoftware.Steam"])
        self.assertEqual(launch_command(apps[0],which=self.which),
                         ("/usr/bin/flatpak","run","org.gimp.GIMP"))
        run.assert_called_once_with(
            ["/usr/bin/flatpak","list","--app","--columns=application,name"],
            capture_output=True,text=True,check=False,timeout=6)

    def test_waydroid_list_and_run(self):
        fake=Mock(returncode=0,stdout="Name: F-Droid\npackageName: org.fdroid.fdroid\n\nName: Calculator\npackageName: com.android.calculator2\n")
        apps=android_apps(which=self.which,run=lambda *a,**k:fake)
        self.assertEqual(len(apps),2)
        self.assertEqual(launch_command(apps[0],which=self.which),
                         ("/usr/bin/waydroid","app","launch","com.android.calculator2"))

    def test_commands_are_explicit_and_interactive(self):
        enable=enable_flathub_command(which=self.which)
        self.assertEqual(enable[:3],("/usr/bin/konsole","-e","/usr/bin/flatpak"))
        self.assertIn("--user",enable)
        install=install_flatpak_command("org.gimp.GIMP",which=self.which)
        self.assertEqual(install,("/usr/bin/konsole","-e","/usr/bin/flatpak","--user",
                                  "install","flathub","org.gimp.GIMP"))
        with self.assertRaises(AppHubError):
            install_flatpak_command("org.gimp.GIMP;rm -rf /",which=self.which)
        with self.assertRaises(AppHubError):
            launch_command(App("Android","Bad","$(whoami)"),which=self.which)
        popen=Mock();start(install,popen=popen)
        popen.assert_called_once_with(list(install),start_new_session=True)

    def test_missing_backends_do_not_break_list(self):
        self.assertEqual(flatpak_apps(which=lambda _:None),[])
        self.assertEqual(android_apps(which=lambda _:None),[])


class RestoreTests(unittest.TestCase):
    @staticmethod
    def which(tool):
        return "/usr/bin/" + tool

    def test_live_detection(self):
        with tempfile.TemporaryDirectory() as root:
            path=Path(root)/"cmdline"
            path.write_text("quiet boot=live splash")
            self.assertTrue(is_live_boot(path))
            path.write_text("quiet")
            self.assertFalse(is_live_boot(path))

    def test_no_timeshift_in_live(self):
        with self.assertRaises(RestoreError):
            restore_command(which=self.which,is_live=True)
        self.assertEqual(restore_command(which=self.which,is_live=False),
                         ("/usr/bin/timeshift-launcher",))

    def test_backups_are_separate(self):
        self.assertEqual(backup_command(which=self.which),("/usr/bin/backintime-qt",))
        with self.assertRaises(RestoreError):
            backup_command(which=lambda _:None)


if __name__ == "__main__":
    unittest.main()
