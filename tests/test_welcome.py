import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from aevonyr.onboarding import onboarding_state_path, completed, mark_completed
from aevonyr.integrations import (
    IntegrationError, TOOLS, tool_command, available_tools,
    paired_device_count, start_tool,
)


class FirstRunTests(unittest.TestCase):
    def test_initially_open_then_completed(self):
        with tempfile.TemporaryDirectory() as root:
            target = Path(root)/"aevonyr"/"welcome-state.json"
            self.assertFalse(completed(target))
            mark_completed(target)
            self.assertTrue(completed(target))
            self.assertEqual(json.loads(target.read_text()), {"completed": True})
            mark_completed(target)
            self.assertTrue(completed(target))
            self.assertFalse(target.with_suffix(".json.tmp").exists())

    def test_corrupt_is_not_complete(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root)/"state.json"
            path.write_text("unreadable{")
            self.assertFalse(completed(path))
            path.write_text('{"completed":"yes"}')
            self.assertFalse(completed(path))

    def test_paths_respect_xdg(self):
        self.assertEqual(onboarding_state_path(environ={"XDG_CONFIG_HOME":"/tmp/xdg"}),
                         Path("/tmp/xdg/aevonyr-os/welcome-state.json"))
        self.assertEqual(onboarding_state_path(environ={},home="/tmp/home"),
                         Path("/tmp/home/.config/aevonyr-os/welcome-state.json"))


class IntegrationsTests(unittest.TestCase):
    def lookup(self, name):
        return "/usr/bin/" + name

    def test_only_whitelisted_commands(self):
        for name in TOOLS:
            cmd = tool_command(name, which=self.lookup)
            self.assertEqual(cmd, ("/usr/bin/" + TOOLS[name].candidates[0],))
        with self.assertRaises(IntegrationError):
            tool_command("rm -rf", which=self.lookup)

    def test_fallback_and_missing(self):
        self.assertEqual(tool_command("phone",
            which=lambda n: "/usr/bin/kdeconnect-app" if n == "kdeconnect-app" else None),
            ("/usr/bin/kdeconnect-app",))
        with self.assertRaises(IntegrationError):
            tool_command("updates", which=lambda n: None)
        self.assertFalse(available_tools(which=lambda n: None)["phone"])

    def test_start_without_shell(self):
        popen = Mock()
        start_tool("updates", which=self.lookup, popen=popen)
        popen.assert_called_once_with(["/usr/bin/plasma-discover"], start_new_session=True)

    def test_count_devices_without_exposing_ids(self):
        run = Mock(return_value=Mock(returncode=0,stdout="aaabbb\ncccddd\n"))
        self.assertEqual(paired_device_count(which=self.lookup, run=run),2)
        run.assert_called_once_with(["/usr/bin/kdeconnect-cli", "--list-devices",
                                     "--id-only"],capture_output=True,text=True,
                                    timeout=6,check=False)
        self.assertIsNone(paired_device_count(which=lambda _:None))
        def fails(*args,**kwargs):
            raise subprocess.TimeoutExpired("kdeconnect-cli", 6)
        self.assertIsNone(paired_device_count(which=self.lookup,run=fails))


if __name__ == "__main__":
    unittest.main()
