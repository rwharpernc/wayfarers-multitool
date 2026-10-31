"""Each mode's sections are shown in alphabetical order of their names.

The order is the order of FEATURES in ui.py, so the test reads that list from the source (importing ui would need EDMC) and
compares each mode's modules, by the name the commander sees, against a sorted copy. A new section needs a row in NAMES.
"""
from __future__ import annotations

import os
import re
import unittest

PLUGIN = os.path.join(os.path.dirname(__file__), "..", "plugin")

# module -> (mode, the name shown for the section)
NAMES = {
    "autohonk": ("exploration", "Auto-Honk"),
    "discovery": ("exploration", "Auto-Honk Discovery Alerts"),      # shares Auto-Honk's row, so it sorts straight after it
    "boxel_survey": ("exploration", "Boxel Survey"),
    "codex_completionist_panel": ("exploration", "Codex Completionist"),
    "surface_compass": ("exploration", "Compass"),
    "explore_dashboard": ("exploration", "Dashboard"),
    "expedition_panel": ("exploration", "Expedition"),
    "landing_finder_panel": ("exploration", "Nearest place to land"),
    "route_planner_panel": ("exploration", "Route Planner"),
    "notes_panel": ("exploration", "Notes"),
    "organic_scan_panel": ("exploration", "Organic Scanning"),
    "poi_reference_panel": ("exploration", "POI Reference"),
    "inventory_panel": ("fieldops", "Inventory"),
    "materials_panel": ("fieldops", "Materials"),
    "screenshots": ("fieldops", "Screenshots"),
    "ship_builds_panel": ("fieldops", "Ship Builds"),
    "trade_panel": ("trade", "Trade"),
    "trade_watch_panel": ("trade", "Watch list"),
}


def features():
    text = open(os.path.join(PLUGIN, "ui.py"), encoding="utf-8").read()
    body = text[text.index("FEATURES = ("):]
    body = body[:body.index("\n)\n")]
    body = re.sub(r"#[^\n]*", "", body)
    return [name for name in re.findall(r"[a-z_]+", body) if name != "FEATURES"]


class PanelOrderTests(unittest.TestCase):
    def test_every_section_is_in_alphabetical_order_within_its_mode(self):
        listed = features()
        for mode in {mode for mode, _name in NAMES.values()}:
            modules = [m for m in listed if m in NAMES and NAMES[m][0] == mode]
            names = [NAMES[m][1] for m in modules]
            self.assertEqual(names, sorted(names, key=str.lower), mode)

    def test_every_listed_section_has_a_name_here(self):
        listed = features()
        for module in NAMES:
            self.assertIn(module, listed)
        for module in listed:
            source = open(os.path.join(PLUGIN, module + ".py"), encoding="utf-8").read() if os.path.exists(os.path.join(PLUGIN, module + ".py")) else ""
            match = re.search(r'^PANEL_PLACEMENT = "(\w+)"', source, re.M)
            if match and match.group(1) in ("exploration", "fieldops", "trade"):
                self.assertIn(module, NAMES, f"{module} is a section in the {match.group(1)} mode; give it a name in NAMES")


if __name__ == "__main__":
    unittest.main()
