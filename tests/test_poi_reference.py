"""POI Reference (poi_reference_panel.py): one FIND POI runs the GEC and Canonn lookups together, and the nearer result is the one copied.

The Collector is the part with logic and no Tk: it waits for every lookup of one FIND POI to end, then names the nearest system.
"""
from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def collector():
    """A Collector built from the class source alone, so no EDMC or Tk module is needed."""
    source = os.path.join(os.path.dirname(__file__), "..", "plugin", "poi_reference_panel.py")
    text = open(source, encoding="utf-8").read()
    start = text.index("class Collector:")
    end = text.index("class PoiReferenceController:")
    namespace = {"Optional": __import__("typing").Optional, "Set": set, "Tuple": tuple}
    exec("from typing import Optional, Set, Tuple\n" + text[start:end], namespace)
    return namespace["Collector"]()


class CollectorTests(unittest.TestCase):
    def test_nothing_is_reported_until_every_lookup_has_ended(self):
        c = collector()
        c.begin({"gec", "canonn"})
        self.assertTrue(c.busy)
        self.assertIsNone(c.report("gec", "Sol", 12.0))
        self.assertTrue(c.busy)
        self.assertEqual(c.report("canonn", "Alpha Centauri", 4.0), "Alpha Centauri")
        self.assertFalse(c.busy)

    def test_the_nearer_system_wins_whichever_source_finishes_first(self):
        c = collector()
        c.begin({"gec", "canonn"})
        c.report("canonn", "Near", 3.0)
        self.assertEqual(c.report("gec", "Far", 90.0), "Near")

    def test_a_source_that_found_nothing_leaves_the_other_result(self):
        c = collector()
        c.begin({"gec", "canonn"})
        c.report("gec", None, None)
        self.assertEqual(c.report("canonn", "Only", 50.0), "Only")

    def test_no_result_from_either_gives_an_empty_name(self):
        c = collector()
        c.begin({"gec"})
        self.assertEqual(c.report("gec", None, None), "")

    def test_a_new_find_forgets_the_last_one(self):
        c = collector()
        c.begin({"gec"})
        c.report("gec", "Old", 1.0)
        c.begin({"gec"})
        self.assertEqual(c.report("gec", "New", 500.0), "New")


class WiringTests(unittest.TestCase):
    def test_the_two_old_sections_are_replaced_by_one_in_the_feature_lists(self):
        root = os.path.join(os.path.dirname(__file__), "..", "plugin")
        for name in ("ui.py", "load.py"):
            text = open(os.path.join(root, name), encoding="utf-8").read()
            self.assertIn("poi_reference_panel", text, name)
            self.assertNotIn("gec_poi_panel,", text, name)
            self.assertNotIn("canonn_poi_panel,", text, name)


if __name__ == "__main__":
    unittest.main()
