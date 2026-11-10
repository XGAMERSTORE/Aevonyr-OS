"""Bookish OS canonical entrypoint smoke tests, no graphical display needed."""
import subprocess
import sys
import unittest


class BookishEntryTests(unittest.TestCase):
    def test_bookish_language_listing(self):
        result = subprocess.run(
            [sys.executable, "-m", "bookish", "--languages"],
            capture_output=True, text=True, timeout=20, check=True,
        )
        self.assertIn("English", result.stdout)

    def test_legacy_entrypoint_remains_compatible(self):
        result = subprocess.run(
            [sys.executable, "-m", "aevonyr", "--languages"],
            capture_output=True, text=True, timeout=20, check=True,
        )
        self.assertIn("English", result.stdout)


if __name__ == "__main__":
    unittest.main()
