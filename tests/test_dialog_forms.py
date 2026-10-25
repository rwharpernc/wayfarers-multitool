"""What the Add/Edit Hotspot and Ship Build forms mean, without a window: the typed text becomes a Hotspot or ShipBuild, or a message says what is wrong (plugin/mining_hotspot_dialog.py,
plugin/ship_builds_dialog.py, plugin/uikit/form.py), (the market research table's rows are in tests/dialog_windows_smoke.py).
Run with: python -m unittest discover -s tests"""

from __future__ import annotations

import os
import sys
import types
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.modules.setdefault("config", types.SimpleNamespace(appname="EDMarketConnector", config=types.SimpleNamespace(get_bool=lambda *a, **k: False, get_str=lambda *a, **k: "")))

from plugin import mining_hotspot_dialog as HD  # noqa: E402
from plugin import ship_builds_dialog as SD  # noqa: E402
from plugin.mining_hotspots import Hotspot  # noqa: E402
from plugin.ship_builds_data import ShipBuild  # noqa: E402
from plugin.uikit import form  # noqa: E402


def hotspot_values(**kw):
    values = {"system": "Sol", "body": "Mars 1", "latitude": "", "longitude": "", "material": "painite", "rigs": "", "signal_number": "", "amount": "", "density": "", "folder": "", "notes": ""}
    values.update(kw)
    return values


class ParseTests(unittest.TestCase):
    def test_blank_is_none_and_text_is_parsed(self) -> None:
        self.assertIsNone(form.parse_optional_int("  ", "Rigs"))
        self.assertEqual(form.parse_optional_int(" 4 ", "Rigs", 1, 7), 4)
        self.assertIsNone(form.parse_optional_float("", "Latitude"))
        self.assertEqual(form.parse_optional_float("-12.5", "Latitude"), -12.5)
        self.assertIsNone(form.blank_to_none("  "))
        self.assertEqual(form.blank_to_none(" High "), "High")

    def test_a_bad_number_names_the_field(self) -> None:
        with self.assertRaisesRegex(ValueError, "Rigs must be a whole number"):
            form.parse_optional_int("two", "Rigs")
        with self.assertRaisesRegex(ValueError, "Rigs must be 1 to 7"):
            form.parse_optional_int("9", "Rigs", 1, 7)
        with self.assertRaisesRegex(ValueError, "Latitude must be a number"):
            form.parse_optional_float("north", "Latitude")


class HotspotFormTests(unittest.TestCase):
    def test_the_material_is_written_in_the_one_spelling(self) -> None:
        self.assertEqual(HD.build_hotspot(hotspot_values(material="  low temperature   diamonds ")).material, "Low Temp. Diamonds")
        self.assertEqual(HD.build_hotspot(hotspot_values(material="painite")).material, "Painite")

    def test_required_fields_and_ranges(self) -> None:
        for blank in ("system", "body", "material"):
            with self.assertRaisesRegex(ValueError, "required"):
                HD.build_hotspot(hotspot_values(**{blank: "  "}))
        with self.assertRaisesRegex(ValueError, "Rigs must be 1 to"):
            HD.build_hotspot(hotspot_values(rigs="0"))
        with self.assertRaisesRegex(ValueError, "Longitude must be a number"):
            HD.build_hotspot(hotspot_values(longitude="east"))

    def test_the_values_arrive_typed(self) -> None:
        spot = HD.build_hotspot(hotspot_values(rigs="5", signal_number="2", latitude="10.5", longitude="-20", amount="High", density="Low", folder=" Gold run ", notes=" a note "))
        self.assertEqual((spot.rigs, spot.signal_number, spot.latitude, spot.longitude, spot.amount, spot.density, spot.folder, spot.notes), (5, 2, 10.5, -20.0, "High", "Low", "Gold run", "a note"))
        plain = HD.build_hotspot(hotspot_values())
        self.assertEqual((plain.rigs, plain.latitude, plain.amount, plain.density), (None, None, None, None))

    def test_an_edit_keeps_what_the_form_does_not_show(self) -> None:
        old = Hotspot(system="Sol", body="Mars 1", material="Painite", mined_tons=120, ground="icy")
        edited = HD.build_hotspot(hotspot_values(notes="changed"), old)
        self.assertEqual((edited.mined_tons, edited.ground, edited.notes), (120, "icy", "changed"))

    def test_the_form_is_filled_from_the_hotspot_or_the_prefill(self) -> None:
        by_key = {f.key: f.value for f in HD.fields_for(None, "Sol", "Mars 1", 10.5, 20.25) if f.key}
        self.assertEqual((by_key["system"], by_key["body"], by_key["latitude"], by_key["longitude"], by_key["rigs"]), ("Sol", "Mars 1", "10.5", "20.25", ""))
        old = Hotspot(system="Alpha", body="A 1", material="Gold", rigs=4, latitude=1.0, longitude=2.0, amount="Low", folder="Mine")
        by_key = {f.key: f.value for f in HD.fields_for(old, "ignored", "ignored") if f.key}
        self.assertEqual((by_key["system"], by_key["material"], by_key["rigs"], by_key["amount"], by_key["folder"]), ("Alpha", "Gold", "4", "Low", "Mine"))


class ShipFormTests(unittest.TestCase):
    VALUES = {"name": "Explorer", "ship": "Anaconda", "role": "", "site": "EDSY", "url": "https://edsy.org/x", "notes": ""}

    def test_a_new_build_gets_an_id_and_an_edit_keeps_it(self) -> None:
        new = SD.build_ship(self.VALUES)
        self.assertTrue(new.id)
        old = ShipBuild(id="abc", ship="Anaconda", name="Old", site="EDSY", url="https://x", created="2026-01-01", updated="2026-02-02")
        edited = SD.build_ship({**self.VALUES, "name": "New"}, old)
        self.assertEqual((edited.id, edited.name, edited.created, edited.updated), ("abc", "New", "2026-01-01", "2026-02-02"))

    def test_required_fields_and_the_link(self) -> None:
        with self.assertRaisesRegex(ValueError, "required"):
            SD.build_ship({**self.VALUES, "name": " "})
        with self.assertRaisesRegex(ValueError, "must start with http"):
            SD.build_ship({**self.VALUES, "url": "edsy.org/x"})


if __name__ == "__main__":
    unittest.main()
