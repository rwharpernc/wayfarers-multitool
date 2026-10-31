"""How an ingredient is got (plugin/ingredient_sources.py), checked against the real unlock ingredients of the engineers, and the guide data (engineer_guides_data.py)."""
from __future__ import annotations

import os
import sys
import types
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
if "config" not in sys.modules:
    _stub = types.ModuleType("config")
    _stub.appname = "EDMarketConnector"
    _stub.config = types.SimpleNamespace(get_str=lambda key, default="": default, get_bool=lambda key, default=False: default, default_journal_dir="")
    sys.modules["config"] = _stub

from plugin import blueprints, engineer_guides_data as G, ingredient_sources as S  # noqa: E402


def unlock_ingredient(engineer: str, name: str) -> blueprints.Ingredient:
    unlock = blueprints.unlock_for(engineer)
    return next(i for i in unlock.ingredients if i.name == name)


class ClassifyTests(unittest.TestCase):
    def test_the_kinds_of_the_real_unlock_items(self):
        expected = {
            ("Chloe Sedesi", "Sensor Fragment"): S.SITE,
            ("Liz Ryder", "Landmines"): S.BUY,
            ("Lei Cheung", "Gold"): S.BUY,                 # at markets and mined: a market is the shorter way
            ("Selene Jean", "Painite"): S.MINE,
            ("Marsha Hicks", "Osmium"): S.MINE,
            ("Etienne Dorn", "Occupied Escape Pod"): S.SPECIAL,
            ("Marco Qwent", "Modular Terminals"): S.SPECIAL,
            ("Kit Fowler", "Push"): S.SETTLEMENT,
            ("Ram Tah", "Classified Scan Databanks"): S.SCAN,
            ("Tiana Fortune", "Decoded Emission Data"): S.SCAN,
        }
        for (engineer, item), kind in expected.items():
            self.assertEqual(S.classify(unlock_ingredient(engineer, item)), kind, f"{engineer}: {item}")

    def test_every_unlock_item_has_a_kind_and_a_label(self):
        for blueprint in blueprints.ALL:
            if not blueprint.is_unlock:
                continue
            for ingredient in blueprint.ingredients:
                kind = S.classify(ingredient)
                self.assertIn(kind, S.LABELS, f"{blueprint.name}: {ingredient.name}")
                self.assertTrue(S.label(kind))

    def test_how_to_get_says_the_kind_and_where(self):
        label, where = S.how_to_get(unlock_ingredient("Chloe Sedesi", "Sensor Fragment"))
        self.assertEqual(label, S.LABELS[S.SITE])
        self.assertIn("Thargoid", where)


class GuideTests(unittest.TestCase):
    def test_no_guides_are_written_yet_and_an_unknown_engineer_has_none(self):
        self.assertIsNone(G.guide_for("nobody"))

    def test_a_guide_is_unconfirmed_until_it_says_otherwise(self):
        guide = G.Guide(summary="Do the thing.", steps=("One", "Two"), cautions=("Mind the corrosion",))
        self.assertFalse(guide.verified)
        self.assertEqual((guide.where, guide.system, guide.updated, guide.items), ("", "", "", ()))

    def test_every_guide_key_is_an_engineer_key(self):
        from plugin import engineers
        for key in G.GUIDES:
            self.assertIsNotNone(engineers.info(key), f"no engineer called {key}")


if __name__ == "__main__":
    unittest.main()
