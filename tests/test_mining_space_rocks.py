"""The Space Mining run keeps the latest prospected rock, counts core asteroids once, and holds the exact limpet count (plugin/mining_space.py with plugin/mining_alerts.py)."""

import os
import sys
import types
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from plugin import mining_alerts, mining_space as S  # noqa: E402


def prospect(repo, materials, core=None, target=("", 20)):
    entry = {"event": "ProspectedAsteroid", "Materials": materials, "Content": "$AsteroidMaterialContent_Low;", "Content_Localised": "Material Content: Low", "Remaining": 100.0}
    if core:
        entry["MotherlodeMaterial"] = core
    repo.record_prospected(entry["Content"], entry["Content_Localised"], materials, mining_alerts.rock_finding(entry, *target))


class SpaceRockTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo = S.SpaceMiningRepository()
        self.repo.set_current_cmdr("Bocheaux")

    def test_cores_are_counted_and_the_last_rock_kept(self) -> None:
        prospect(self.repo, [{"Name": "water", "Proportion": 23.6}], core="Bromellite")
        prospect(self.repo, [{"Name": "iron", "Proportion": 5.0}])
        run = self.repo.current_run()
        self.assertEqual((run.cores_found, run.last_core), (1, "Bromellite"))
        self.assertEqual(run.last_rock.materials, (("Iron", 5.0),))
        self.assertEqual(run.prospected_count, 2)

    def test_the_same_rock_twice_counts_one_core(self) -> None:
        for _ in range(2):
            prospect(self.repo, [{"Name": "water", "Proportion": 23.6}], core="Bromellite")
        run = self.repo.current_run()
        self.assertEqual((run.cores_found, run.prospected_count, run.duplicate_prospected), (1, 1, 1))

    def test_the_panel_and_history_share_one_key(self) -> None:
        from plugin import mining_history
        self.assertIs(S.prospect_key, mining_alerts.prospect_key)
        self.assertIs(mining_history.prospect_key, mining_alerts.prospect_key)

    def test_a_run_with_only_a_core_has_data(self) -> None:
        self.assertFalse(self.repo.current_run().has_data())
        prospect(self.repo, [], core="Painite")
        self.assertTrue(self.repo.current_run().has_data())

    def test_the_exact_limpet_count(self) -> None:
        self.assertIsNone(self.repo.current_run().limpets_aboard)
        self.repo.update_limpets(7)
        self.assertEqual(self.repo.current_run().limpets_aboard, 7)
        self.repo.update_limpets(None)
        self.assertEqual(self.repo.current_run().limpets_aboard, 7, "an unknown count does not wipe a known one")

    def test_a_new_run_starts_clean(self) -> None:
        prospect(self.repo, [], core="Painite")
        self.repo.start_new_run()
        run = self.repo.current_run()
        self.assertEqual((run.cores_found, run.last_core, run.last_rock), (0, "", None))


class LimpetLineTests(unittest.TestCase):
    """The panel and the HUD word the limpets aboard through one function (plugin/mining_render.py)."""

    def test_exact_count_then_estimate_then_nothing(self) -> None:
        sys.modules.setdefault("config", types.SimpleNamespace(appname="EDMarketConnector"))
        from plugin import mining_render
        run = S.SpaceMiningRun()
        self.assertEqual(mining_render.limpets_on_board(run), "")
        run.limpets_bought, run.limpets_launched = 10, {"Collection": 3}
        self.assertEqual(mining_render.limpets_on_board(run), "~7")
        run.limpets_aboard = 4
        self.assertEqual(mining_render.limpets_on_board(run), "4")          # the exact count wins, as on the panel
        run.limpets_aboard, run.limpets_bought = 0, 0
        self.assertEqual(mining_render.limpets_on_board(run), "0")


if __name__ == "__main__":
    unittest.main()
