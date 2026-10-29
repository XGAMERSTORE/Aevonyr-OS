import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock
from aevonyr.compat import CompatibilityError, execute_plan, make_plan
from aevonyr.i18n import CATALOG, LANGUAGES, normalize_language, tr

class Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)

    def file(self, name):
        p = self.base / name
        p.write_bytes(b"test")
        return p

    def resolver(self, name):
        return "/usr/bin/" + name

    def test_translations(self):
        self.assertEqual(tr("home"), "Home")
        self.assertEqual(tr("home", "cs-CZ"), "Domů")
        self.assertEqual(tr("windows_desc", "fr"), CATALOG["en"]["windows_desc"])
        self.assertEqual(normalize_language("xx"), "en")
        self.assertEqual(len(LANGUAGES), 10)

    def test_exe(self):
        path = self.file("test app.EXE")
        plan = make_plan(path, which=self.resolver)
        self.assertEqual(plan.command, ("/usr/bin/wine", str(path)))
        fake = Mock()
        execute_plan(plan, popen=fake)
        fake.assert_called_once_with(["/usr/bin/wine", str(path)], start_new_session=True)

    def test_msi(self):
        path = self.file("setup.msi")
        self.assertEqual(make_plan(path, which=self.resolver).command,
                         ("/usr/bin/wine", "msiexec", "/i", str(path)))

    def test_apk(self):
        path = self.file("app.apk")
        plan = make_plan(path, which=self.resolver)
        self.assertEqual(plan.kind, "apk-install")
        self.assertEqual(plan.command, ("/usr/bin/waydroid", "app", "install", str(path)))

    def test_failures(self):
        with self.assertRaises(CompatibilityError):
            make_plan(self.file("test.exe"), which=lambda _: None)
        with self.assertRaises(CompatibilityError):
            make_plan(self.file("test.sh"), which=self.resolver)
        with self.assertRaises(CompatibilityError):
            make_plan(self.base / "missing.apk", which=self.resolver)

if __name__ == "__main__":
    unittest.main()
