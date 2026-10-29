"""Unit tests for plugin/mining_alerts.py: reading a prospected rock (core and target), the page's rock line, the exact limpet count from EDMC's cargo, and when the limpet and
hold alerts apply. No network and no EDMC."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from plugin import mining_alerts as M  # noqa: E402

ROCK = {"event": "ProspectedAsteroid", "Materials": [{"Name": "Uraninite", "Name_Localised": "Uraninite", "Proportion": 9.2}, {"Name": "painite", "Proportion": 34.4}],
        "Content": "$AsteroidMaterialContent_High;", "Content_Localised": "Material Content: High", "Remaining": 100.0}
CORE = {"event": "ProspectedAsteroid", "Materials": [{"Name": "water", "Proportion": 23.6}], "MotherlodeMaterial": "Bromellite",
        "Content": "$AsteroidMaterialContent_Low;", "Content_Localised": "Material Content: Low", "Remaining": 100.0}


class RockFindingTests(unittest.TestCase):
    def test_materials_come_richest_first_with_the_games_names(self) -> None:
        found = M.rock_finding(ROCK)
        self.assertEqual(found.materials, (("Painite", 34.4), ("Uraninite", 9.2)))
        self.assertEqual((found.grade, found.remaining, found.core, found.target), ("High", 100.0, None, None))

    def test_a_core_asteroid_names_its_mineral(self) -> None:
        found = M.rock_finding(CORE)
        self.assertEqual(found.core, "Bromellite")
        self.assertEqual(M.rock_alert(found).lines, ("Core asteroid", "Bromellite"))
        self.assertEqual(M.rock_alert(found).kind, M.KIND_CORE)

    def test_the_target_needs_the_percent(self) -> None:
        self.assertEqual(M.rock_finding(ROCK, "painite", 30).target, ("Painite", 34.4))     # case does not matter
        self.assertIsNone(M.rock_finding(ROCK, "Painite", 40).target)
        self.assertIsNone(M.rock_finding(ROCK, "", 1).target)                                  # no target chosen
        self.assertIsNone(M.rock_finding(ROCK, "Platinum", 1).target)
        alert = M.rock_alert(M.rock_finding(ROCK, "Painite", 30))
        self.assertEqual((alert.kind, alert.lines), (M.KIND_TARGET, ("Rich rock: Painite", "34% of the rock")))

    def test_an_ordinary_rock_raises_no_alert(self) -> None:
        self.assertIsNone(M.rock_alert(M.rock_finding(ROCK, "Platinum", 20)))

    def test_damaged_events_do_not_fail(self) -> None:
        found = M.rock_finding({"event": "ProspectedAsteroid", "Materials": [None, {"Name": "x"}, {"Name": "y", "Proportion": "z"}]})
        self.assertEqual((found.materials, found.core, found.grade), ((), None, "?"))
        self.assertIn("no materials", M.rock_text(found))

    def test_the_page_line(self) -> None:
        self.assertEqual(M.rock_text(M.rock_finding(ROCK, "Painite", 30)), "Last rock: Painite 34%, Uraninite 9% (High), target: Painite")
        self.assertEqual(M.rock_text(M.rock_finding(CORE)), "Last rock: Water 24% (Low), core: Bromellite")
        self.assertEqual(M.rock_text(M.rock_finding(CORE), last_core="Bromellite"), "Last rock: Water 24% (Low)")      # the Core asteroids line names it
        self.assertEqual(M.rock_text(M.rock_finding(CORE), last_core="Painite"), "Last rock: Water 24% (Low), core: Bromellite")


class LimpetsTests(unittest.TestCase):
    def test_limpets_are_the_drones_in_the_cargo(self) -> None:
        self.assertEqual(M.limpets_aboard({"Cargo": {"drones": 12, "gold": 3}}), 12)
        self.assertEqual(M.limpets_aboard({"Cargo": {"gold": 3}}), 0)
        self.assertIsNone(M.limpets_aboard({}))
        self.assertIsNone(M.limpets_aboard(None))


class WatcherTests(unittest.TestCase):
    def setUp(self) -> None:
        self.at = 1000.0
        self.watcher = M.MiningWatcher(now=lambda: self.at, target=lambda: ("Painite", 30))

    def test_a_rock_alert_lasts_thirty_seconds(self) -> None:
        self.watcher.handle_event(CORE)
        self.assertEqual([a.kind for a in self.watcher.alerts()], [M.KIND_CORE])
        self.at += M.ROCK_ALERT_S + 1
        self.assertEqual(self.watcher.alerts(), [])
        self.watcher.handle_event(ROCK)
        self.assertEqual([a.kind for a in self.watcher.alerts()], [M.KIND_TARGET])
        self.watcher.handle_event({"event": "ProspectedAsteroid", "Materials": [{"Name": "iron", "Proportion": 5}]})   # an ordinary rock clears it
        self.assertEqual(self.watcher.alerts(), [])
        self.assertEqual(self.watcher.last_rock.materials, (("Iron", 5.0),))

    def test_limpets_and_hold_only_while_mining(self) -> None:
        self.watcher.handle_event({"event": "Loadout", "CargoCapacity": 100})
        self.watcher.handle_event({"event": "Cargo", "Vessel": "Ship", "Count": 97}, {"Cargo": {"drones": 3}})
        self.assertEqual(self.watcher.alerts(), [], "not mining: no alert, however full")
        self.watcher.handle_event({"event": "LaunchDrone", "Type": "Collection"}, {"Cargo": {"drones": 3}})
        found = {a.kind: a.lines for a in self.watcher.alerts(limpets_low=5, hold_percent=95)}
        self.assertEqual(found[M.KIND_LIMPETS], ("Low on limpets", "3 aboard"))
        self.assertEqual(found[M.KIND_HOLD], ("Hold nearly full", "97 of 100 t"))
        self.assertEqual(list(self.watcher.alerts(limpets_low=2, hold_percent=98)), [], "under both thresholds")
        self.at += M.ACTIVE_S + 1
        self.assertEqual(self.watcher.alerts(), [], "mining stopped long ago")

    def test_limpets_unknown_until_edmc_says(self) -> None:
        self.watcher.handle_event({"event": "MiningRefined", "Type": "painite"})
        self.assertEqual(self.watcher.alerts(), [])
        self.assertIsNone(self.watcher.limpets)


LOADOUT_WITH_CONTROLLER = {"event": "Loadout", "CargoCapacity": 100, "Modules": [{"Slot": "Slot01", "Item": "int_dronecontrol_prospector_size3_class5"}]}
LOADOUT_WITHOUT = {"event": "Loadout", "CargoCapacity": 100, "Modules": [{"Slot": "Slot01", "Item": "int_refinery_size3_class5"}, {"Slot": "Slot02", "Item": "int_cargorack_size5_class1"}]}
REFINED = {"event": "MiningRefined", "Type": "painite"}
NO_DRONES = {"Cargo": {"gold": 3}}


class LimpetAlertAppliesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.at = 1000.0
        self.watcher = M.MiningWatcher(now=lambda: self.at, target=lambda: ("", 20))

    def kinds(self):
        return [a.kind for a in self.watcher.alerts()]

    def test_a_laser_miner_with_no_limpets_is_never_told_they_are_out(self) -> None:
        self.watcher.handle_event(LOADOUT_WITHOUT, NO_DRONES)
        self.watcher.handle_event(REFINED, NO_DRONES)
        self.assertNotIn(M.KIND_LIMPETS, self.kinds())

    def test_no_loadout_and_no_limpets_seen_means_no_alert(self) -> None:
        self.watcher.handle_event(REFINED, NO_DRONES)
        self.assertEqual(self.watcher.limpets, 0)
        self.assertNotIn(M.KIND_LIMPETS, self.kinds())

    def test_a_fitted_controller_alerts_even_at_zero(self) -> None:
        self.watcher.handle_event(LOADOUT_WITH_CONTROLLER, NO_DRONES)
        self.watcher.handle_event(REFINED, NO_DRONES)
        self.assertIn(M.KIND_LIMPETS, self.kinds())

    def test_limpets_seen_aboard_start_the_alert_without_a_loadout(self) -> None:
        self.watcher.handle_event({"event": "LaunchDrone", "Type": "Collection"}, {"Cargo": {"drones": 4}})
        self.assertIn(M.KIND_LIMPETS, self.kinds())
        self.watcher.handle_event({"event": "LaunchDrone", "Type": "Collection"}, NO_DRONES)
        self.assertIn(M.KIND_LIMPETS, self.kinds(), "running out is what the alert is for")

    def test_a_new_loadout_without_a_controller_forgets_the_old_ship(self) -> None:
        self.watcher.handle_event(LOADOUT_WITH_CONTROLLER, {"Cargo": {"drones": 4}})
        self.watcher.handle_event(LOADOUT_WITHOUT, NO_DRONES)
        self.watcher.handle_event(REFINED, NO_DRONES)
        self.assertNotIn(M.KIND_LIMPETS, self.kinds())

    def test_never_while_a_rhino_is_out(self) -> None:
        self.watcher.handle_event(LOADOUT_WITH_CONTROLLER, {"Cargo": {"drones": 2}})
        self.watcher.handle_event({"event": "LaunchSRV", "SRVType": "mev_rhino"}, {"Cargo": {"drones": 2}})
        self.watcher.handle_event(REFINED, {"Cargo": {"drones": 2}})
        self.assertNotIn(M.KIND_LIMPETS, self.kinds())
        self.watcher.handle_event({"event": "DockSRV", "SRVType": "mev_rhino"}, {"Cargo": {"drones": 2}})
        self.assertIn(M.KIND_LIMPETS, self.kinds())

    def test_a_rhino_cargo_event_counts_as_a_rhino_out(self) -> None:
        self.watcher.handle_event(LOADOUT_WITH_CONTROLLER, {"Cargo": {"drones": 2}})
        self.watcher.handle_event({"event": "Cargo", "Vessel": "SRV", "Count": 1}, {"Cargo": {"drones": 2}})
        self.watcher.handle_event(REFINED, {"Cargo": {"drones": 2}})
        self.assertNotIn(M.KIND_LIMPETS, self.kinds())
        self.watcher.handle_event({"event": "Cargo", "Vessel": "Ship", "Count": 1}, {"Cargo": {"drones": 2}})
        self.assertIn(M.KIND_LIMPETS, self.kinds())

    def test_the_threshold_setting_still_applies(self) -> None:
        self.watcher.handle_event(LOADOUT_WITH_CONTROLLER, {"Cargo": {"drones": 9}})
        self.watcher.handle_event(REFINED, {"Cargo": {"drones": 9}})
        self.assertEqual(self.watcher.alerts(limpets_low=5), [])
        self.assertEqual([a.kind for a in self.watcher.alerts(limpets_low=9)], [M.KIND_LIMPETS])

    def test_fits_controller_reads_the_modules(self) -> None:
        self.assertTrue(M.fits_controller(LOADOUT_WITH_CONTROLLER))
        self.assertTrue(M.fits_controller({"Modules": [{"Item": "Int_DroneControl_Collection_Size1_Class1"}]}))
        self.assertFalse(M.fits_controller(LOADOUT_WITHOUT))
        self.assertFalse(M.fits_controller({"Modules": [{"Item": "int_dronecontrol_fueltransfer_size1_class1"}]}))
        self.assertFalse(M.fits_controller({"Modules": "x"}))
        self.assertFalse(M.fits_controller({}))


class TargetNameTests(unittest.TestCase):
    def test_every_spelling_of_the_target_matches_the_rock(self) -> None:
        opal = {"event": "ProspectedAsteroid", "Materials": [{"Name": "Opal", "Name_Localised": "Void Opal", "Proportion": 25.0}], "Remaining": 100.0}
        for typed in ("Void Opals", "Void Opal", "void opals", "opal"):
            self.assertEqual(M.rock_finding(opal, typed, 20).target, ("Void Opal", 25.0), typed)
        diamonds = {"event": "ProspectedAsteroid", "Materials": [{"Name": "lowtemperaturediamond", "Name_Localised": "Low Temp. Diamonds", "Proportion": 25.0}]}
        for typed in ("Low Temperature Diamonds", "Low Temp. Diamonds", "LowTemperatureDiamond"):
            self.assertEqual(M.rock_finding(diamonds, typed, 20).target, ("Low Temp. Diamonds", 25.0), typed)
        self.assertIsNone(M.rock_finding(opal, "Painite", 20).target)


class RockRepeatTests(unittest.TestCase):
    def setUp(self) -> None:
        self.at = 1000.0
        self.watcher = M.MiningWatcher(now=lambda: self.at, target=lambda: ("Painite", 30))

    def test_the_same_rock_again_does_not_alert_again(self) -> None:
        self.watcher.handle_event(ROCK)
        self.assertEqual(len(self.watcher.alerts()), 1)
        self.at += M.ROCK_ALERT_S + 1
        self.assertEqual(self.watcher.alerts(), [])
        self.watcher.handle_event(ROCK)                       # a re-prospect of the same rock after the alert ran out
        self.assertEqual(self.watcher.alerts(), [])

    def test_a_repeat_does_not_clear_the_alert_showing(self) -> None:
        self.watcher.handle_event(ROCK)
        self.watcher.handle_event(ROCK)
        self.assertEqual([a.kind for a in self.watcher.alerts()], [M.KIND_TARGET])

    def test_a_new_run_forgets_the_rocks(self) -> None:
        self.watcher.handle_event(ROCK)
        self.at += M.ROCK_ALERT_S + 1
        self.watcher.handle_event({"event": "Undocked"})
        self.watcher.handle_event(ROCK)
        self.assertEqual([a.kind for a in self.watcher.alerts()], [M.KIND_TARGET])

    def test_a_mostly_used_up_rock_raises_no_rich_rock_alert(self) -> None:
        self.watcher.handle_event(dict(ROCK, Remaining=M.MIN_REMAINING_PERCENT - 1))
        self.assertEqual(self.watcher.alerts(), [])
        self.watcher.handle_event(dict(ROCK, Remaining=M.MIN_REMAINING_PERCENT, Materials=[{"Name": "painite", "Proportion": 35.0}]))
        self.assertEqual([a.kind for a in self.watcher.alerts()], [M.KIND_TARGET])

    def test_a_core_is_still_announced_when_little_is_left(self) -> None:
        self.watcher.handle_event(dict(CORE, Remaining=5.0))
        self.assertEqual([a.kind for a in self.watcher.alerts()], [M.KIND_CORE])

    def test_the_alert_carries_the_rock_for_the_sound_key(self) -> None:
        self.watcher.handle_event(ROCK)
        self.assertEqual(self.watcher.alerts()[0].rock, M.prospect_key(ROCK["Materials"]))
        self.assertIsNotNone(M.prospect_key(ROCK["Materials"]))
        self.assertIsNone(M.prospect_key([]))
        self.assertEqual(M.prospect_key([{"Name": "A", "Proportion": 1.04}]), M.prospect_key([{"Name": "a", "Proportion": 1.0}]))


class ClampTests(unittest.TestCase):
    def test_clamp(self) -> None:
        self.assertEqual(M.clamp("25", 1, 100, 20), 25)
        self.assertEqual(M.clamp("500", 1, 100, 20), 100)
        self.assertEqual(M.clamp("-3", 1, 100, 20), 1)
        self.assertEqual(M.clamp("x", 1, 100, 20), 20)


if __name__ == "__main__":
    unittest.main()
