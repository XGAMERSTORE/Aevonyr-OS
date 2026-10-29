import unittest
from unittest.mock import Mock, patch
from tempfile import TemporaryDirectory
from pathlib import Path
from aevonyr.diagnostics import android_state, live_mode, diagnose, format_report
from aevonyr.session import SessionError, command_for, execute_action

class DiagnosticsTests(unittest.TestCase):
    def test_android_running(self):
        runner=Mock(return_value=Mock(returncode=0,stdout="Session: RUNNING\nContainer: RUNNING\n"))
        self.assertEqual(android_state(which=lambda _: "/usr/bin/waydroid",run=runner,
                           environ={"XDG_SESSION_TYPE":"wayland"}),"Running")
        runner.assert_called_once_with(["/usr/bin/waydroid","status"],capture_output=True,
                                       text=True,timeout=5,check=False)
    def test_android_missing_and_wayland(self):
        self.assertEqual(android_state(which=lambda _: None),"Not installed")
        self.assertEqual(android_state(which=lambda _: "/usr/bin/waydroid",
                         environ={"XDG_SESSION_TYPE":"x11"}),"Wayland session required")
    def test_live_mode(self):
        with TemporaryDirectory() as directory:
            file=Path(directory)/"cmdline"
            file.write_text("quiet boot=live")
            self.assertEqual(live_mode(file),"Live")
            file.write_text("quiet")
            self.assertEqual(live_mode(file),"Installed / other")
    def test_report(self):
        with patch("aevonyr.diagnostics.android_state",return_value="Running"), \
             patch("aevonyr.diagnostics.network_status",return_value="full"):
            report=diagnose(which=lambda x: "/usr/bin/"+x)
        self.assertIn("Wine: Installed",format_report(report))
        self.assertEqual(report["Internet connectivity"],"full")

class SessionTests(unittest.TestCase):
    def lookup(self,name):return "/usr/bin/"+name
    def test_session(self):
        self.assertEqual(command_for("lock",which=self.lookup),
                         ["/usr/bin/loginctl","lock-session"])
        self.assertEqual(command_for("logout",which=self.lookup),
                         ["/usr/bin/qdbus6","org.kde.Shutdown","/Shutdown","logout"])
        self.assertEqual(command_for("reboot",which=self.lookup),
                         ["/usr/bin/systemctl","reboot"])
        self.assertEqual(command_for("poweroff",which=self.lookup),
                         ["/usr/bin/systemctl","poweroff"])
        self.assertEqual(command_for("logout",which=lambda x: "/usr/bin/loginctl" if x=="loginctl" else None,
                         environ={"XDG_SESSION_ID":"42"}),
                         ["/usr/bin/loginctl","terminate-session","42"])
    def test_no_shell(self):
        p=Mock()
        execute_action("lock",which=self.lookup,popen=p)
        p.assert_called_once_with(["/usr/bin/loginctl","lock-session"],start_new_session=True)
        with self.assertRaises(SessionError):
            command_for("rm",which=self.lookup)

if __name__=="__main__":
    unittest.main()
