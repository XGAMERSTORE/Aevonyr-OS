"""Installable language-pack regression tests."""
import json
import tempfile
import unittest
from pathlib import Path
from aevonyr.i18n import CATALOG, LANGUAGES, install_language_pack, load_language_packs, missing_keys, normalize_language, tr


class LanguagePackTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.src = self.root / "nl.json"
        self.src.write_text(json.dumps({"locale": "nl-NL", "name": "Nederlands", "strings": {"home": "Start", "settings": "Instellingen"}}), encoding="utf-8")

    def tearDown(self):
        CATALOG.pop("nl-nl", None)
        LANGUAGES.pop("nl-nl", None)

    def test_install_and_fallback(self):
        code = install_language_pack(self.src, directory=self.root / "installed")
        self.assertEqual(code, "nl-nl")
        self.assertEqual(tr("settings", "nl-NL"), "Instellingen")
        self.assertEqual(tr("windows_desc", "nl-NL"), CATALOG["en"]["windows_desc"])
        self.assertIn("windows_desc", missing_keys(code))
        self.assertEqual(normalize_language("nl_NL"), "nl-nl")
        self.assertTrue((self.root / "installed" / "nl-nl.json").exists())

    def test_reload(self):
        install_language_pack(self.src, directory=self.root / "installed")
        CATALOG.pop("nl-nl")
        LANGUAGES.pop("nl-nl")
        self.assertEqual(load_language_packs(self.root / "installed"), ["nl-nl"])

    def test_malformed_rejected(self):
        self.src.write_text('{"locale":"../en","name":"bad","strings":{}}')
        with self.assertRaises(ValueError):
            install_language_pack(self.src, directory=self.root / "installed")
        self.src.write_text("x" * (256 * 1024 + 1))
        with self.assertRaises(ValueError):
            install_language_pack(self.src, directory=self.root / "installed")

    def test_invalid_does_not_block_valid(self):
        directory = self.root / "installed"
        directory.mkdir()
        (directory / "broken.json").write_text("{bad")
        (directory / "nl.json").write_bytes(self.src.read_bytes())
        self.assertEqual(load_language_packs(directory), ["nl-nl"])


if __name__ == "__main__":
    unittest.main()
