"""One spelling for a mineral or commodity name in the mining books (plugin/mining_names.py)."""
import unittest

from plugin import mining_names as N
from plugin import mining_rings_data as RD
from plugin.mining_history import _commodity


class NormalizeTests(unittest.TestCase):
    def test_capitals_and_internal_names(self) -> None:
        self.assertEqual(N.normalize("tritium"), "Tritium")
        self.assertEqual(N.normalize("Liquid oxygen"), "Liquid Oxygen")
        self.assertEqual(N.normalize("  methanol  monohydrate crystals "), "Methanol Monohydrate Crystals")
        self.assertEqual(N.normalize("$painite_name;"), "Painite")
        self.assertEqual(N.normalize("lowtemperaturediamond"), "Low Temp. Diamonds")
        self.assertEqual(N.normalize("Low Temp. Diamonds"), "Low Temp. Diamonds")
        self.assertEqual(N.normalize("Opal"), "Void Opal")
        self.assertEqual(N.normalize(""), "")
        self.assertEqual(N.normalize(None), "")

    def test_the_journal_names_a_run_records(self) -> None:
        self.assertEqual(_commodity({"Type": "tritium"}), "Tritium")
        self.assertEqual(_commodity({"Type": "lowtemperaturediamond", "Type_Localised": "Low Temp. Diamonds"}), "Low Temp. Diamonds")
        self.assertEqual(_commodity({}), "Unknown")

    def test_methods_agree_on_every_spelling(self) -> None:
        from plugin import mining_methods as MM
        for name in ("Void Opals", "Void Opal", "void opals", "opal"):
            self.assertEqual(MM.methods_for(name), (MM.CORE,), name)
        for name in ("Low Temperature Diamonds", "Low Temp. Diamonds", "LowTemperatureDiamond", "lowtemperaturediamonds"):
            self.assertEqual(MM.methods_for(name), (MM.CORE, MM.LASER_SURFACE, MM.SUBSURFACE), name)
        self.assertEqual(MM.methods_for(N.normalize("Void Opals")), (MM.CORE,))       # the Mining pages look up a normalized name
        self.assertEqual(MM.methods_for("painite"), (MM.CORE, MM.LASER_SURFACE, MM.SUBSURFACE))
        self.assertEqual(MM.methods_for("Gold"), (MM.LASER_SURFACE,))

    def test_every_listed_commodity_reaches_the_same_methods_in_any_spelling(self) -> None:
        from plugin import mining_methods as MM
        from plugin import mining_spansh_client as SC
        for name in SC.KNOWN_MINING_COMMODITIES:       # the autocomplete spelling and the canonical one agree
            self.assertEqual(N.normalize(N.normalize(name)), N.normalize(name), name)
            self.assertEqual(MM.methods_for(name), MM.methods_for(N.normalize(name)), name)

    def test_ring_hotspots_use_one_spelling(self) -> None:
        self.assertEqual(RD.hotspots_from([{"Type": "tritium", "Count": 2}, {"Type_Localised": "Tritium", "Count": 3}, {"Type": "$SAA_SignalType_Biological;", "Count": 1}]), {"Tritium": 3})
        rows = RD.build_rows({"r": {**RD.new_ring("A 1 A Ring"), "hotspots": {"tritium": 2, "Tritium": 1, "Void Opal": 5}}}, [], {})
        self.assertEqual(rows[0].hotspots, {"Tritium": 2, "Void Opal": 5})


if __name__ == "__main__":
    unittest.main()
