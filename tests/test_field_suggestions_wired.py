"""Every box that takes a name WFMT can list has its suggestions attached. Read from the source (importing the windows would need EDMC and Tk), so a box
that is rebuilt without them fails here and not in the game."""
from __future__ import annotations

import os
import unittest

PLUGIN = os.path.join(os.path.dirname(__file__), "..", "plugin")

# file -> what its name box must call
WIRED = {
    "expedition_window.py": ("system_autocomplete.attach(system_entry", "name_suggestions.attach_bodies(body_entry"),
    "trade_windows.py": ("system_autocomplete.attach(entry, var, provider=self._controller.start_suggestions)",),
    "materials_window.py": ("name_suggestions.attach_names(search, self._query",),
    "blueprints_window.py": ("name_suggestions.attach_names(search, self._query, blueprints.search_names)",),
    "inventory_window.py": ("name_suggestions.attach_names(filter_box, self._filter_var",),
    "ship_modules_tab.py": ("name_suggestions.attach_names(box, self._query, self._module_names)",),
}


class FieldSuggestionsWired(unittest.TestCase):
    def test_each_name_box_calls_its_suggestions(self) -> None:
        for name, calls in WIRED.items():
            text = open(os.path.join(PLUGIN, name), encoding="utf-8").read()
            for call in calls:
                self.assertIn(call, text, f"{name} lost {call}")

    def test_the_system_history_hands_its_systems_to_the_suggestions(self) -> None:
        text = open(os.path.join(PLUGIN, "system_history.py"), encoding="utf-8").read()
        self.assertIn("system_names.set_visited(self.names())", text)
        self.assertGreaterEqual(text.count("self._publish()"), 2, "when a commander takes over, and when the read finishes")


if __name__ == "__main__":
    unittest.main()
