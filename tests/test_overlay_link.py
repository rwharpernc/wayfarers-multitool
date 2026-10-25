"""overlay_link: the notice that EDMCModernOverlay is not installed shows only when it is the overlay in use and nothing of it is found."""
import os
import sys
import tempfile
import types
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

sys.modules.setdefault("myNotebook", mock.MagicMock())
sys.modules.setdefault("ttkHyperlinkLabel", mock.MagicMock())
if "config" not in sys.modules:
    _stub = types.ModuleType("config")
    _stub.appname = "EDMarketConnector"
    _stub.config = mock.MagicMock()
    sys.modules["config"] = _stub

from plugin import overlay_link as L  # noqa: E402


class FoundTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.plugins = self._tmp.name
        self.wfmt = os.path.join(self.plugins, "Wayfarers-Multitool")
        os.makedirs(self.wfmt)

    def test_not_found_when_only_wfmt_is_installed(self):
        self.assertFalse(L.modern_overlay_found(self.wfmt))

    def test_found_when_its_folder_sits_beside_wfmt(self):
        os.makedirs(os.path.join(self.plugins, "EDMCModernOverlay"))
        self.assertTrue(L.modern_overlay_found(self.wfmt))

    def test_found_whatever_the_folder_is_called_in_case(self):
        os.makedirs(os.path.join(self.plugins, "edmcmodernoverlay-main"))
        self.assertTrue(L.modern_overlay_found(self.wfmt))

    def test_a_file_with_that_name_is_not_the_plugin(self):
        with open(os.path.join(self.plugins, "EDMCModernOverlay.txt"), "w") as handle:
            handle.write("x")
        self.assertFalse(L.modern_overlay_found(self.wfmt))


class MissingTests(unittest.TestCase):
    def test_missing_needs_the_modern_overlay_in_use_and_not_found(self):
        for wanted, found, expected in ((True, False, True), (True, True, False), (False, False, False), (False, True, False)):
            with self.subTest(wanted=wanted, found=found):
                with mock.patch.object(L, "wanted", return_value=wanted), mock.patch.object(L, "modern_overlay_found", return_value=found):
                    self.assertEqual(L.missing(), expected)

    def test_the_message_says_what_to_install(self):
        self.assertIn("EDMCModernOverlay", L.NOT_FOUND)
        self.assertIn("Linux", L.NOT_FOUND)


if __name__ == "__main__":
    unittest.main()
