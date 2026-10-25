"""Every request WFMT makes to Spansh goes through the courtesy layer (plugin/spansh_courtesy.py).

The layer spaces requests out, retries them politely and stops asking when Spansh keeps failing, and it can only do that if no module reaches Spansh another way. This scans
the plugin's source: a module that names a Spansh API address must use `spansh_courtesy`, and no module but the layer itself may open a connection to Spansh directly.
It reads files only, so it behaves the same on Windows and Linux.
"""
from __future__ import annotations

import os
import re
import unittest

PLUGIN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "plugin")
SPANSH_API = re.compile(r"https?://(?:www\.)?spansh\.co\.uk/api", re.IGNORECASE)
DIRECT_OPEN = re.compile(r"\burlopen\s*\(|\bbuild_opener\s*\(")

# Modules that mention a Spansh address without sending a request to it (they only describe or link to it).
DESCRIPTION_ONLY = {
    "settings_online.py",
    "issue_report.py",
    "carrier_route.py",
}


def _modules():
    for name in sorted(os.listdir(PLUGIN)):
        if name.endswith(".py"):
            with open(os.path.join(PLUGIN, name), encoding="utf-8") as handle:
                yield name, handle.read()


class SpanshThroughCourtesyTests(unittest.TestCase):
    def test_a_module_that_calls_a_spansh_api_uses_the_courtesy_layer(self) -> None:
        missing = [name for name, text in _modules()
                   if name != "spansh_courtesy.py" and name not in DESCRIPTION_ONLY and SPANSH_API.search(text) and "spansh_courtesy" not in text]
        self.assertEqual(missing, [], "these modules name a Spansh API address but do not use spansh_courtesy: " + ", ".join(missing))

    def test_no_module_opens_a_connection_to_spansh_by_itself(self) -> None:
        offenders = [name for name, text in _modules()
                     if name != "spansh_courtesy.py" and SPANSH_API.search(text) and DIRECT_OPEN.search(text)]
        self.assertEqual(offenders, [], "these modules name a Spansh API address and also open a connection themselves: " + ", ".join(offenders))

    def test_the_layer_itself_still_exists(self) -> None:
        self.assertTrue(os.path.isfile(os.path.join(PLUGIN, "spansh_courtesy.py")))


if __name__ == "__main__":
    unittest.main()
