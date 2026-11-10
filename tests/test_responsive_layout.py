"""Display-independent responsive Bookish layout tests."""
import unittest

from aevonyr.layout import layout_for_width


class ResponsiveLayoutTests(unittest.TestCase):
    def test_desktop_navigation(self):
        profile = layout_for_width(1240)
        self.assertEqual(profile["mode"], "desktop")
        self.assertTrue(profile["label_navigation"])
        self.assertEqual(profile["sidebar_width"], 225)

    def test_tablet_navigation(self):
        profile = layout_for_width(800)
        self.assertEqual(profile["mode"], "compact")
        self.assertFalse(profile["label_navigation"])
        self.assertEqual(profile["sidebar_width"], 74)

    def test_breakpoint(self):
        self.assertEqual(layout_for_width(899)["mode"], "compact")
        self.assertEqual(layout_for_width(900)["mode"], "desktop")

    def test_invalid_width(self):
        with self.assertRaises(ValueError):
            layout_for_width(0)


if __name__ == "__main__":
    unittest.main()
