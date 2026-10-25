"""Get body info (plugin/mining_body_lookup.py): EDSM's and Spansh's bodies become the Mining body list, known body sizes and mining-location counts without overriding the journal. Pure logic:
no Tk, no network (the Spansh request is replaced), no EDMC."""

import json
import os
import sys
import types
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
_cfg = sys.modules.setdefault("config", types.SimpleNamespace(appname="EDMarketConnector"))
if not hasattr(_cfg, "config"):
    _cfg.config = types.SimpleNamespace(get_bool=lambda key, default=False: default)
for _attr, _default in (("appname", "EDMarketConnector"), ("user_agent", "WFMT-test"), ("appversion", lambda: "5.13.0")):
    if not hasattr(_cfg, _attr):
        setattr(_cfg, _attr, _default)

from plugin import mining_body_lookup as lookup  # noqa: E402
from plugin import mining_ground  # noqa: E402
from plugin import mining_surface as surface_mining  # noqa: E402
from plugin import spansh_courtesy  # noqa: E402
from plugin.mining_body_survey import SystemBodySurvey  # noqa: E402

SYSTEM = "Pegasi Sector KO-E a13-2"
MINING = surface_mining.MINING_LOCATION_SIGNAL_TYPE
# The shape of a live answer from EDSM's api-system-v1/bodies (radius in kilometers), trimmed to the fields used.
EDSM = [
    {"name": SYSTEM, "type": "Star", "subType": "L (Brown dwarf) Star", "isLandable": None, "radius": None, "volcanismType": None},
    {"name": f"{SYSTEM} 1", "type": "Planet", "subType": "Icy body", "isLandable": True, "radius": 6354.9035, "volcanismType": "Major Water Magma"},
    {"name": f"{SYSTEM} 2", "type": "Planet", "subType": "Icy body", "isLandable": True, "radius": 6485.063, "volcanismType": "Major Water Magma"},
    {"name": f"{SYSTEM} 3", "type": "Planet", "subType": "Rocky body", "isLandable": True, "radius": 5311.441, "volcanismType": "No volcanism"},
    {"name": f"{SYSTEM} 5", "type": "Planet", "subType": "Icy body", "isLandable": False, "radius": 7759.6875, "volcanismType": "Water Geysers"},
    {"name": f"{SYSTEM} 6", "type": "Planet", "subType": "High metal content world", "isLandable": True, "radius": 4853.928, "volcanismType": "Minor Silicate Vapour Geysers"},
]
# The shape of a live answer from Spansh's api/dump/<id64>: the system, with each body's signals (the mining location count under its own key).
SPANSH = {"system": {"name": SYSTEM, "id64": 1, "bodies": [
    {"name": f"{SYSTEM} 2", "type": "Planet", "subType": "Icy body", "isLandable": True, "radius": 6485.063, "volcanismType": "Major Water Magma",
     "signals": {"genuses": [], "signals": {MINING: 12, "$SAA_SignalType_Geological;": 2}, "updateTime": "2026-10-13 03:29:27+00"}},
    {"name": f"{SYSTEM} 3", "type": "Planet", "subType": "Rocky body", "isLandable": True, "radius": 5311.441, "volcanismType": "No volcanism", "signals": None},
    {"name": f"{SYSTEM} 4", "type": "Planet", "subType": "Icy body", "isLandable": True, "radius": 5402.456, "volcanismType": "No volcanism",
     "signals": {"signals": {"$SAA_SignalType_Geological;": 1}}},
    {"name": f"{SYSTEM} 5", "type": "Planet", "subType": "Icy body", "isLandable": False, "radius": 7759.6875, "signals": {"signals": {MINING: 3}}},
]}}


class EdsmParseTests(unittest.TestCase):
    def test_only_landable_planets_are_kept_in_order(self) -> None:
        self.assertEqual([b.name for b in lookup.parse_edsm(EDSM)], [f"{SYSTEM} 1", f"{SYSTEM} 2", f"{SYSTEM} 3", f"{SYSTEM} 6"])

    def test_the_radius_is_in_meters_and_there_is_no_count(self) -> None:
        second = lookup.parse_edsm(EDSM)[1]
        self.assertAlmostEqual(second.radius_m, 6485063.0, places=3)
        self.assertIsNone(second.mining_locations)

    def test_no_volcanism_is_none_and_other_volcanism_is_kept(self) -> None:
        bodies = {b.name: b for b in lookup.parse_edsm(EDSM)}
        self.assertIsNone(bodies[f"{SYSTEM} 3"].volcanism)
        self.assertEqual(bodies[f"{SYSTEM} 2"].volcanism, "Major Water Magma")

    def test_the_kind_gives_the_same_ground_as_the_journals_class_would(self) -> None:
        bodies = {b.name: b for b in lookup.parse_edsm(EDSM)}
        self.assertEqual(mining_ground.classify(bodies[f"{SYSTEM} 2"].planet_class, bodies[f"{SYSTEM} 2"].volcanism), "icy")
        self.assertEqual(mining_ground.classify(bodies[f"{SYSTEM} 3"].planet_class, bodies[f"{SYSTEM} 3"].volcanism), "rocky")
        self.assertEqual(mining_ground.classify(bodies[f"{SYSTEM} 6"].planet_class, bodies[f"{SYSTEM} 6"].volcanism), "high_metal")

    def test_damaged_entries_are_skipped_not_raised(self) -> None:
        raw = [None, "x", 5, {}, {"type": "Planet", "isLandable": True}, {"type": "Planet", "isLandable": True, "name": "  ", "subType": "Icy body"},
               {"type": "Planet", "isLandable": True, "name": "A 1", "subType": ""}, {"type": "Planet", "isLandable": "yes", "name": "A 2", "subType": "Icy body"},
               {"type": "Planet", "isLandable": True, "name": "A 3", "subType": "Icy body", "radius": "far"},
               {"type": "Planet", "isLandable": True, "name": "A 4", "subType": "Icy body", "radius": -5}]
        parsed = lookup.parse_edsm(raw)
        self.assertEqual([b.name for b in parsed], ["A 3", "A 4"])
        self.assertTrue(all(b.radius_m is None for b in parsed))

    def test_nothing_gives_nothing(self) -> None:
        self.assertEqual(lookup.parse_edsm(None), [])
        self.assertEqual(lookup.parse_edsm([]), [])


class SpanshParseTests(unittest.TestCase):
    def test_the_mining_location_count_is_read_from_the_signals(self) -> None:
        bodies = {b.name: b for b in lookup.parse_spansh(SPANSH)}
        self.assertEqual(bodies[f"{SYSTEM} 2"].mining_locations, 12)
        self.assertIsNone(bodies[f"{SYSTEM} 3"].mining_locations, "no signals at all")
        self.assertIsNone(bodies[f"{SYSTEM} 4"].mining_locations, "signals, but no mining locations")

    def test_a_body_that_is_not_landable_is_left_out(self) -> None:
        self.assertNotIn(f"{SYSTEM} 5", [b.name for b in lookup.parse_spansh(SPANSH)])

    def test_the_system_itself_is_read_as_well_as_one_inside_a_system_key(self) -> None:
        self.assertEqual(lookup.parse_spansh(SPANSH["system"]), lookup.parse_spansh(SPANSH))

    def test_damaged_answers_give_nothing(self) -> None:
        for raw in (None, [], "x", {}, {"system": {}}, {"system": {"bodies": "no"}}, {"bodies": [None, 3]}):
            self.assertEqual(lookup.parse_spansh(raw), [], repr(raw))

    def test_a_bad_count_is_ignored(self) -> None:
        raw = {"bodies": [{"name": "A 1", "type": "Planet", "isLandable": True, "subType": "Icy body", "signals": {"signals": {MINING: "many"}}},
                          {"name": "A 2", "type": "Planet", "isLandable": True, "subType": "Icy body", "signals": {"signals": {MINING: -1}}},
                          {"name": "A 3", "type": "Planet", "isLandable": True, "subType": "Icy body", "signals": {"signals": {MINING: True}}}]}
        self.assertTrue(all(b.mining_locations is None for b in lookup.parse_spansh(raw)))


class MergeTests(unittest.TestCase):
    def test_the_first_source_wins_and_the_second_fills_in_the_count_and_the_rest(self) -> None:
        merged = {b.name: b for b in lookup.merge(lookup.parse_edsm(EDSM), lookup.parse_spansh(SPANSH))}
        self.assertEqual(merged[f"{SYSTEM} 2"].mining_locations, 12)
        self.assertEqual(merged[f"{SYSTEM} 2"].planet_class, "Icy body")
        self.assertIn(f"{SYSTEM} 4", merged, "a body only the second source has is added")
        self.assertEqual(len(merged), 5)

    def test_the_order_is_the_first_sources_then_the_new_ones(self) -> None:
        names = [b.name for b in lookup.merge(lookup.parse_edsm(EDSM), lookup.parse_spansh(SPANSH))]
        self.assertEqual(names, [f"{SYSTEM} 1", f"{SYSTEM} 2", f"{SYSTEM} 3", f"{SYSTEM} 6", f"{SYSTEM} 4"])

    def test_the_first_sources_values_are_not_replaced(self) -> None:
        first = [lookup.OutsideBody("A 1", "Icy body", None, 1000.0, 2)]
        second = [lookup.OutsideBody("a 1", "Rocky body", "Major", 9999.0, 7)]
        self.assertEqual(lookup.merge(first, second), first)

    def test_either_side_may_be_empty(self) -> None:
        bodies = lookup.parse_spansh(SPANSH)
        self.assertEqual(lookup.merge([], bodies), bodies)
        self.assertEqual(lookup.merge(bodies, []), bodies)


class FetchTests(unittest.TestCase):
    def test_without_an_address_nothing_is_asked(self) -> None:
        with mock.patch.object(spansh_courtesy, "call") as call:
            self.assertIsNone(lookup.fetch_spansh(None))
            self.assertIsNone(lookup.fetch_spansh(0))
            call.assert_not_called()

    def test_the_dump_is_asked_for_by_the_address_and_parsed(self) -> None:
        with mock.patch.object(spansh_courtesy, "call", return_value=json.dumps(SPANSH).encode("utf-8")) as call:
            self.assertEqual(lookup.fetch_spansh(12345), SPANSH)
        request = call.call_args[0][0]
        self.assertTrue(request.full_url.endswith("/api/dump/12345"))

    def test_any_failure_gives_none_not_an_exception(self) -> None:
        with self.assertLogs(lookup.logger, level="WARNING"):
            for error in (spansh_courtesy.SpanshBusy("paused"), OSError("down"), ValueError("x")):
                with mock.patch.object(spansh_courtesy, "call", side_effect=error):
                    self.assertIsNone(lookup.fetch_spansh(1), repr(error))
            with mock.patch.object(spansh_courtesy, "call", return_value=b"not json"):
                self.assertIsNone(lookup.fetch_spansh(1))
        with mock.patch.object(spansh_courtesy, "call", return_value=b"[1, 2]"):
            self.assertIsNone(lookup.fetch_spansh(1))


class ApplyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.survey = SystemBodySurvey()
        self.survey.on_system_changed(SYSTEM)
        self.surface = surface_mining.SurfaceMiningRepository()
        self.bodies = lookup.merge(lookup.parse_edsm(EDSM), lookup.parse_spansh(SPANSH))

    def test_the_bodies_sizes_and_counts_are_added(self) -> None:
        applied = lookup.apply(SYSTEM, self.bodies, self.survey, self.surface)
        self.assertEqual((applied.landable, applied.bodies_added, applied.sizes_added, applied.counts_added), (5, 5, 5, 1))
        listed = {b.name: b for b in self.survey.landable_bodies()}
        self.assertEqual(listed[f"{SYSTEM} 2"].planet_class, "Icy body")
        self.assertEqual(listed[f"{SYSTEM} 2"].mining_signal_count, 12)
        self.assertIsNone(listed[f"{SYSTEM} 3"].mining_signal_count)
        self.assertAlmostEqual(self.surface.known_radius(f"{SYSTEM} 2"), 6485063.0, places=3)

    def test_what_the_journal_gave_is_not_overwritten(self) -> None:
        self.survey.record_scan(SYSTEM, f"{SYSTEM} 2", "Icy body", "journal volcanism", True)
        self.survey.record_signal(SYSTEM, f"{SYSTEM} 2", 3)
        self.surface.record_body_radius(f"{SYSTEM} 2", 6485000.0)
        applied = lookup.apply(SYSTEM, self.bodies, self.survey, self.surface)
        self.assertEqual((applied.bodies_added, applied.sizes_added, applied.counts_added), (4, 4, 0))
        kept = next(b for b in self.survey.landable_bodies() if b.name == f"{SYSTEM} 2")
        self.assertEqual((kept.volcanism, kept.mining_signal_count), ("journal volcanism", 3))
        self.assertEqual(self.surface.known_radius(f"{SYSTEM} 2"), 6485000.0)

    def test_a_second_lookup_adds_nothing(self) -> None:
        lookup.apply(SYSTEM, self.bodies, self.survey, self.surface)
        again = lookup.apply(SYSTEM, self.bodies, self.survey, self.surface)
        self.assertEqual((again.bodies_added, again.sizes_added, again.counts_added), (0, 0, 0))

    def test_a_survey_with_no_system_yet_is_told_this_one(self) -> None:
        fresh = SystemBodySurvey()
        lookup.apply(SYSTEM, self.bodies, fresh, self.surface)
        self.assertEqual(fresh.current_system, SYSTEM)
        self.assertEqual(len(fresh.landable_bodies()), 5)

    def test_a_survey_on_another_system_gets_the_sizes_only(self) -> None:
        elsewhere = SystemBodySurvey()
        elsewhere.on_system_changed("Somewhere Else")
        applied = lookup.apply(SYSTEM, self.bodies, elsewhere, self.surface)
        self.assertEqual((applied.bodies_added, applied.sizes_added, applied.counts_added), (0, 5, 0))
        self.assertEqual(elsewhere.landable_bodies(), [])


class MessageTests(unittest.TestCase):
    def test_what_the_status_line_says(self) -> None:
        self.assertIn("No landable bodies found", lookup.message(SYSTEM, lookup.Applied(0, 0, 0)))
        self.assertIn("Spansh needs the system's id", lookup.message(SYSTEM, lookup.Applied(0, 0, 0), address_known=False))
        self.assertIn("already gave WFMT all of it", lookup.message(SYSTEM, lookup.Applied(4, 0, 0)))
        text = lookup.message(SYSTEM, lookup.Applied(4, 3, 1, 2))
        self.assertIn("added 3 to the list, 1 size and 2 mining-location counts.", text)
        self.assertIn("Journal data was left as it was", text)
        self.assertIn("1 landable body listed", lookup.message(SYSTEM, lookup.Applied(1, 1, 1)))
        self.assertIn("Spansh was not asked", lookup.message(SYSTEM, lookup.Applied(4, 3, 1), address_known=False))


if __name__ == "__main__":
    unittest.main()
