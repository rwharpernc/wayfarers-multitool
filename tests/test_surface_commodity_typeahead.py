"""Commodity type-ahead: the provider path of system_autocomplete.Autocomplete, commodity_autocomplete, the form's "commodity" field kind and the Add/Edit Hotspot form's Contains field
(plugin/commodity_autocomplete.py, plugin/system_autocomplete.py, plugin/uikit/form.py, plugin/mining_hotspot_dialog.py). No Tk window and no EDMC: the suggestion logic is called directly."""

import os
import sys
import types
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

_config = types.ModuleType("config")
_config.appname = "EDMarketConnector"
_config.user_agent = "WFMT-test"
_config.appversion = lambda: "5.13.0"
_config.config = mock.MagicMock()


class _Any(types.ModuleType):
    def __getattr__(self, name):
        if name.startswith("__"):
            raise AttributeError(name)
        return mock.MagicMock()


sys.modules.setdefault("config", _config)
for _attr, _default in (("appname", "EDMarketConnector"), ("user_agent", "WFMT-test"), ("appversion", lambda: "5.13.0")):
    if not hasattr(sys.modules["config"], _attr):
        setattr(sys.modules["config"], _attr, _default)
if not hasattr(sys.modules["config"], "config"):
    sys.modules["config"].config = mock.MagicMock()
for _name in ("monitor", "plug", "EDMCLogging", "l10n", "killswitch", "requests", "ttkHyperlinkLabel", "theme", "myNotebook"):
    sys.modules.setdefault(_name, _Any(_name))

from plugin import mining_hotspot_dialog  # noqa: E402
from plugin import mining_spansh_client  # noqa: E402
from plugin import system_autocomplete  # noqa: E402
from plugin import trade_commodities  # noqa: E402


def autocomplete(text, provider):
    """An Autocomplete with no widget behind it: only matches() is used."""
    box = system_autocomplete.Autocomplete.__new__(system_autocomplete.Autocomplete)
    box._provider = provider
    box._text = lambda: text
    return box


class ProviderTests(unittest.TestCase):
    def test_the_provider_is_the_whole_source_of_suggestions(self) -> None:
        self.assertEqual(autocomplete("pa", lambda text: ["Painite", "Palladium"]).matches(), ["Painite", "Palladium"])

    def test_an_exact_match_is_not_offered_back(self) -> None:
        self.assertEqual(autocomplete("painite", lambda text: ["Painite", "Palladium"]).matches(), ["Palladium"])

    def test_the_provider_gets_the_typed_text(self) -> None:
        seen = []
        autocomplete("plat", lambda text: seen.append(text) or []).matches()
        self.assertEqual(seen, ["plat"])


class CommodityTests(unittest.TestCase):
    def test_suggest_leads_with_names_that_start_with_the_text(self) -> None:
        names = trade_commodities.suggest("pal", (), limit=16)
        self.assertIn("Palladium", names)
        self.assertTrue(all("pal" in name.casefold() for name in names))

    def test_the_known_mining_commodities_are_all_suggestible(self) -> None:
        offered = trade_commodities.suggest("", mining_spansh_client.KNOWN_MINING_COMMODITIES, limit=100)
        self.assertGreater(len(offered), 0)


class HotspotFormTests(unittest.TestCase):
    def test_the_contains_field_is_a_commodity_field_with_preferred_names(self) -> None:
        fields = mining_hotspot_dialog.fields_for(None, materials=["Painite", "Platinum"])
        material = next(field for field in fields if field.key == "material")
        self.assertEqual(material.kind, "commodity")
        self.assertEqual(material.values, ["Painite", "Platinum"])

    def test_the_preferred_names_are_unique_and_include_the_known_commodities(self) -> None:
        with mock.patch.object(mining_hotspot_dialog.hotspot_repository, "materials", return_value=["Painite", "Painite"]):
            names = mining_hotspot_dialog.preferred_materials()
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(names[0], "Painite")
        for known in mining_spansh_client.KNOWN_MINING_COMMODITIES:
            self.assertIn(known, names)


if __name__ == "__main__":
    unittest.main()
