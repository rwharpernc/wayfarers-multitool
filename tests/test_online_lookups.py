"""The online switches as data (online_lookups.py): whether one is on, and the warning a feature shows where it is used when the switch it needs is off."""
from __future__ import annotations

import os
import sys
import types
import unittest
import unittest.mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

SAVED = {}

if "config" not in sys.modules:
    _stub = types.ModuleType("config")
    _stub.appname = "EDMarketConnector"  # type: ignore[attr-defined]
    _stub.config = types.SimpleNamespace(get_bool=lambda key, default=False: SAVED.get(key, default), get_str=lambda *_a, **_k: "", default_journal_dir="")
    sys.modules["config"] = _stub

from plugin import online_lookups as L  # noqa: E402


class OnlineLookupsTests(unittest.TestCase):
    def setUp(self):
        SAVED.clear()
        self._patch = unittest.mock.patch.object(L, "config", types.SimpleNamespace(get_bool=lambda key, default=False: SAVED.get(key, default)))
        self._patch.start()
        self.addCleanup(self._patch.stop)

    def test_a_switch_is_off_until_turned_on_except_the_ones_that_ship_on(self):
        self.assertFalse(L.is_on("wfmt_trade_lookups_enabled"))
        self.assertTrue(L.is_on("wfmt_bgs_tick_enabled"), "tick detection ships on")
        SAVED["wfmt_trade_lookups_enabled"] = True
        self.assertTrue(L.is_on("wfmt_trade_lookups_enabled"))

    def test_the_warning_is_there_only_while_the_switch_is_off(self):
        text = L.needs("wfmt_trade_lookups_enabled")
        self.assertIn("Settings > Online", text)
        self.assertIn("Spansh", text)
        self.assertIn("Trade", text)
        SAVED["wfmt_trade_lookups_enabled"] = True
        self.assertEqual(L.needs("wfmt_trade_lookups_enabled"), "", "on: nothing to warn about")

    def test_a_switch_that_ships_on_warns_once_it_is_turned_off(self):
        self.assertEqual(L.needs("wfmt_bgs_tick_enabled"), "")
        SAVED["wfmt_bgs_tick_enabled"] = False
        self.assertIn("tick", L.needs("wfmt_bgs_tick_enabled").lower())

    def test_a_misspelled_key_fails_loudly_instead_of_never_warning(self):
        with self.assertRaises(KeyError):
            L.needs("wfmt_trade_lookups_enabld")
        with self.assertRaises(KeyError):
            L.is_on("nonsense")

    def test_a_place_that_offers_several_lookups_names_the_ones_that_are_off(self):
        keys = ["wfmt_mining_spansh_hotspot_finder_enabled", "wfmt_mining_spansh_price_finder_enabled", "wfmt_mining_edsm_reserve_lookup_enabled"]
        text = L.needs_any(keys)
        self.assertTrue(text.startswith("These need lookups that are off:"))
        self.assertIn("Spansh", text)
        self.assertIn("EDSM", text)
        self.assertIn("Settings > Online", text)
        SAVED[keys[0]] = SAVED[keys[1]] = True
        self.assertEqual(L.needs_any(keys), L.needs(keys[2]), "one left off: its own warning, in the one wording")
        SAVED[keys[2]] = True
        self.assertEqual(L.needs_any(keys), "", "all on: nothing")
        self.assertEqual(L.needs_any([]), "")

    def test_every_switch_has_a_warning_and_a_default(self):
        for what, _service, key, default, _where in L.LOOKUPS:
            self.assertEqual(L.is_on(key), default, what)
            self.assertEqual(bool(L.needs(key)), not default, what)
        self.assertEqual(set(L.defaults()), {entry[2] for entry in L.LOOKUPS})


if __name__ == "__main__":
    import unittest.mock  # noqa: F401
    unittest.main()
