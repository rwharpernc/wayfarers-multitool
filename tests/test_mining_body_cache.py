"""What Get body info found, kept between sessions (plugin/mining_body_cache.py), and bringing the Mining body list back from it and from the saved System targets survey
(mining_body_lookup.seed, mining_body_survey.seed_from_system_survey). No Tk, no network, no EDMC."""

import json
import os
import shutil
import sys
import tempfile
import types
import unittest
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
_cfg = sys.modules.setdefault("config", types.SimpleNamespace(appname="EDMarketConnector"))
if not hasattr(_cfg, "config"):
    _cfg.config = types.SimpleNamespace(get_bool=lambda key, default=False: default)
for _attr, _default in (("appname", "EDMarketConnector"), ("user_agent", "WFMT-test"), ("appversion", lambda: "5.13.0")):
    if not hasattr(_cfg, _attr):
        setattr(_cfg, _attr, _default)

from plugin import mining_body_cache as cache_module  # noqa: E402
from plugin import mining_body_lookup as lookup  # noqa: E402
from plugin import mining_body_survey as body_survey  # noqa: E402
from plugin import mining_surface as surface_mining  # noqa: E402

SYSTEM = "Pegasi Sector KO-E a13-2"
BODIES = [lookup.OutsideBody(f"{SYSTEM} 2", "Icy body", "Major Water Magma", 6485063.0, 12), lookup.OutsideBody(f"{SYSTEM} 3", "Rocky body", None, 5311441.0, None)]
WHEN = datetime(2026, 10, 20, 12, 0, tzinfo=timezone.utc)


class CacheTests(unittest.TestCase):
    def setUp(self) -> None:
        self.folder = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.folder, True)
        self.cache = cache_module.BodyCache()
        self.cache.load(self.folder)
        self.cache.set_commander("Alpha")

    def reloaded(self, cmdr: str = "Alpha") -> cache_module.BodyCache:
        again = cache_module.BodyCache()
        again.load(self.folder)
        again.set_commander(cmdr)
        return again

    def test_what_was_found_is_remembered_with_its_date(self) -> None:
        self.cache.remember(SYSTEM, BODIES, WHEN)
        self.assertEqual(self.cache.bodies_for(SYSTEM), BODIES)
        self.assertEqual(self.cache.asked(SYSTEM), "2026-10-20")
        self.assertEqual(self.cache.bodies_for(SYSTEM.upper()), BODIES, "the system name is matched without regard to case")

    def test_it_survives_a_restart(self) -> None:
        self.cache.remember(SYSTEM, BODIES, WHEN)
        self.assertEqual(self.reloaded().bodies_for(SYSTEM), BODIES)

    def test_each_commander_has_their_own(self) -> None:
        self.cache.remember(SYSTEM, BODIES, WHEN)
        self.assertEqual(self.reloaded("Beta").bodies_for(SYSTEM), [])
        self.assertEqual(self.reloaded("alpha").bodies_for(SYSTEM), BODIES, "a commander is matched without regard to case")

    def test_the_file_name_names_no_commander(self) -> None:
        self.cache.remember(SYSTEM, BODIES, WHEN)
        self.assertEqual(os.listdir(self.folder), [cache_module.STATE_FILENAME])
        self.assertNotIn("alpha", cache_module.STATE_FILENAME.lower())

    def test_a_new_lookup_replaces_the_old_one_and_is_the_newest(self) -> None:
        self.cache.remember(SYSTEM, BODIES, WHEN)
        self.cache.remember("Other", BODIES[:1], WHEN)
        self.cache.remember(SYSTEM, BODIES[:1], WHEN)
        self.assertEqual(self.cache.bodies_for(SYSTEM), BODIES[:1])
        self.assertEqual(list(self.cache._systems), ["other", SYSTEM.casefold()])

    def test_only_the_newest_systems_are_kept(self) -> None:
        for number in range(cache_module.MAX_SYSTEMS + 5):
            self.cache.remember(f"System {number}", BODIES, WHEN)
        self.assertEqual(len(self.cache._systems), cache_module.MAX_SYSTEMS)
        self.assertEqual(self.cache.bodies_for("System 0"), [])
        self.assertEqual(self.cache.bodies_for(f"System {cache_module.MAX_SYSTEMS + 4}"), BODIES)

    def test_nothing_is_kept_for_no_bodies_no_system_or_no_commander(self) -> None:
        self.cache.remember(SYSTEM, [], WHEN)
        self.cache.remember("", BODIES, WHEN)
        fresh = cache_module.BodyCache()
        fresh.load(self.folder)
        fresh.remember(SYSTEM, BODIES, WHEN)
        self.assertEqual((self.cache.bodies_for(SYSTEM), fresh.bodies_for(SYSTEM)), ([], []))
        self.assertEqual(os.listdir(self.folder), [])

    def test_the_most_bodies_kept_for_a_system_is_capped(self) -> None:
        many = [lookup.OutsideBody(f"B {n}", "Icy body", None, 1000.0) for n in range(cache_module.MAX_BODIES + 30)]
        self.cache.remember(SYSTEM, many, WHEN)
        self.assertEqual(len(self.cache.bodies_for(SYSTEM)), cache_module.MAX_BODIES)

    def test_damaged_entries_are_skipped_and_an_unreadable_file_is_empty(self) -> None:
        self.cache.remember(SYSTEM, BODIES, WHEN)
        path = os.path.join(self.folder, cache_module.STATE_FILENAME)
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
        data["commanders"]["alpha"]["data"]["systems"][SYSTEM.casefold()]["bodies"] += [None, {"name": ""}, {"name": "X"}, {"name": "Y", "planet_class": "Icy body", "radius_m": "big", "mining_locations": -3}]
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(data, handle)
        names = [b.name for b in self.reloaded().bodies_for(SYSTEM)]
        self.assertEqual(names, [f"{SYSTEM} 2", f"{SYSTEM} 3", "Y"])
        self.assertIsNone(self.reloaded().bodies_for(SYSTEM)[-1].radius_m)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("not json")
        self.assertEqual(self.reloaded().bodies_for(SYSTEM), [])


class FakeShared:
    def __init__(self, name, bodies):
        self.name, self.bodies = name, {n: b for n, b in enumerate(bodies)}


def shared_body(name, kind="planet", landable=True, planet_class="Icy body", volcanism="", scanned=True, known=False):
    return types.SimpleNamespace(name=name, kind=kind, landable=landable, planet_class=planet_class, volcanism=volcanism, scanned=scanned, known=known)


class SeedTests(unittest.TestCase):
    def setUp(self) -> None:
        self.survey = body_survey.SystemBodySurvey()
        self.survey.on_system_changed(SYSTEM)
        self.surface = surface_mining.SurfaceMiningRepository()

    def names(self):
        return [b.name for b in self.survey.landable_bodies()]

    def test_landable_scanned_or_known_planets_of_the_shared_survey_are_added(self) -> None:
        shared = FakeShared(SYSTEM, [shared_body("A 1"), shared_body("A 2", scanned=False, known=True, volcanism="minor"), shared_body("A 3", scanned=False, known=False),
                                      shared_body("Star", kind="star"), shared_body("A 5", landable=False), shared_body("A 6", planet_class="")])
        self.assertEqual(body_survey.seed_from_system_survey(self.survey, shared), 2)
        self.assertEqual(sorted(self.names()), ["A 1", "A 2"])

    def test_a_body_the_journal_gave_is_left_alone(self) -> None:
        self.survey.record_scan(SYSTEM, "A 1", "Rocky body", "journal", True)
        self.assertEqual(body_survey.seed_from_system_survey(self.survey, FakeShared(SYSTEM, [shared_body("A 1", planet_class="Icy body")])), 0)
        self.assertEqual(self.survey.landable_bodies()[0].planet_class, "Rocky body")

    def test_another_system_adds_nothing_and_none_at_all_adopts_the_shared_one(self) -> None:
        self.assertEqual(body_survey.seed_from_system_survey(self.survey, FakeShared("Elsewhere", [shared_body("E 1")])), 0)
        fresh = body_survey.SystemBodySurvey()
        self.assertEqual(body_survey.seed_from_system_survey(fresh, FakeShared(SYSTEM, [shared_body("A 1")])), 1)
        self.assertEqual(fresh.current_system, SYSTEM)
        self.assertEqual(body_survey.seed_from_system_survey(fresh, FakeShared("", [])), 0)

    def test_the_system_name_is_matched_without_regard_to_case(self) -> None:
        self.assertEqual(body_survey.seed_from_system_survey(self.survey, FakeShared(SYSTEM.upper(), [shared_body("A 1")])), 1)

    def test_seeding_brings_the_remembered_lookup_back_too(self) -> None:
        folder = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, folder, True)
        remembered = cache_module.BodyCache()
        remembered.load(folder)
        remembered.set_commander("Alpha")
        remembered.remember(SYSTEM, BODIES, WHEN)
        shared = FakeShared(SYSTEM, [shared_body("A 1")])
        added = lookup.seed(SYSTEM, self.survey, self.surface, shared, remembered)
        self.assertEqual(added, 3)
        self.assertEqual(sorted(self.names()), sorted(["A 1"] + [b.name for b in BODIES]))
        self.assertAlmostEqual(self.surface.known_radius(f"{SYSTEM} 2"), 6485063.0)
        self.assertEqual(next(b for b in self.survey.landable_bodies() if b.name == f"{SYSTEM} 2").mining_signal_count, 12)
        self.assertEqual(lookup.seed(SYSTEM, self.survey, self.surface, shared, remembered), 0, "a second seeding adds nothing")

    def test_the_journal_wins_over_a_remembered_lookup_that_arrives_first(self) -> None:
        folder = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, folder, True)
        remembered = cache_module.BodyCache()
        remembered.load(folder)
        remembered.set_commander("Alpha")
        remembered.remember(SYSTEM, BODIES, WHEN)
        lookup.seed(SYSTEM, self.survey, self.surface, None, remembered)
        self.survey.record_scan(SYSTEM, f"{SYSTEM} 2", "Icy body", "from the journal", True)
        self.survey.record_signal(SYSTEM, f"{SYSTEM} 2", 11)
        body = next(b for b in self.survey.landable_bodies() if b.name == f"{SYSTEM} 2")
        self.assertEqual((body.volcanism, body.mining_signal_count), ("from the journal", 11))

    def test_nothing_known_adds_nothing(self) -> None:
        self.assertEqual(lookup.seed(SYSTEM, self.survey, self.surface), 0)
        self.assertEqual(lookup.seed(None, self.survey, self.surface, None, cache_module.BodyCache()), 0)


if __name__ == "__main__":
    unittest.main()
