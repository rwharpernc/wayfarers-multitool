"""Archiving finished construction sites (colonization.Site.archived, SiteRepository.set_archived, colonization_archive_window's figures)."""
from __future__ import annotations

import os
import sys
import tempfile
import types
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
if "config" not in sys.modules:
    _stub = types.ModuleType("config")
    _stub.appname = "EDMarketConnector"
    _stub.config = types.SimpleNamespace(get_str=lambda key: "", default_journal_dir="")
    sys.modules["config"] = _stub

from plugin import colonization as C, colonization_data as D  # noqa: E402


def depot(market_id=1, complete=False, failed=False, stamp="2026-10-01T10:00:00Z"):
    return {"event": "ColonisationConstructionDepot", "timestamp": stamp, "MarketID": market_id, "ConstructionProgress": 1.0 if complete else 0.3,
            "ConstructionComplete": complete, "ConstructionFailed": failed,
            "ResourcesRequired": [{"Name": "$steel_name;", "Name_Localised": "Steel", "RequiredAmount": 500, "ProvidedAmount": 500 if complete else 100}]}


def site(market_id=1, complete=False, failed=False):
    return C.apply_depot_event(depot(market_id, complete, failed), None, name="Orbital Construction Site: Dolgov Depot", system="HIP 34457")


class ArchiveTests(unittest.TestCase):
    def test_the_flag_survives_a_save_and_a_load(self):
        done = site(complete=True)
        done.archived = True
        self.assertTrue(C.Site.from_dict(done.to_dict()).archived)
        self.assertFalse(C.Site.from_dict(site().to_dict()).archived)

    def test_only_a_finished_site_can_be_archived_and_it_can_be_restored(self):
        repo = D.SiteRepository()
        repo.upsert("Alice", site(1, complete=True))
        repo.upsert("Alice", site(2, failed=True))
        repo.upsert("Alice", site(3))
        self.assertEqual(repo.set_archived("alice", [1, 2, 3], True), 2)
        self.assertEqual({s.market_id for s in repo.for_cmdr("Alice") if s.archived}, {1, 2})
        self.assertFalse(repo.get("Alice", 3).archived)
        self.assertEqual(repo.set_archived("Alice", [1, 2], True), 0)          # already archived: nothing changes
        self.assertEqual(repo.set_archived("Alice", [1], False), 1)
        self.assertFalse(repo.get("Alice", 1).archived)

    def test_archiving_saves_once_notifies_and_is_per_commander(self):
        with tempfile.TemporaryDirectory() as folder:
            repo = D.SiteRepository()
            repo.load(folder)
            repo.upsert("Alice", site(1, complete=True))
            repo.upsert("Bob", site(1, complete=True))
            told = []
            repo.add_listener(lambda: told.append(1))
            repo.set_archived("Alice", [1], True)
            self.assertEqual(len(told), 1)
            again = D.SiteRepository()
            again.load(folder)
            self.assertTrue(again.get("Alice", 1).archived)
            self.assertFalse(again.get("Bob", 1).archived)

    def test_a_depot_report_of_work_under_way_takes_a_site_out_of_the_archive(self):
        done = site(1, failed=True)
        done.archived = True
        reopened = C.apply_depot_event(depot(1), done)
        self.assertFalse(reopened.archived)
        still_done = site(2, complete=True)
        still_done.archived = True
        self.assertTrue(C.apply_depot_event(depot(2, complete=True, stamp="2026-10-02T10:00:00Z"), still_done).archived)


class WindowFigureTests(unittest.TestCase):
    def test_the_rows_and_the_summary(self):
        from plugin import colonization_archive as A
        done = C.apply_depot_event(depot(1, complete=True, stamp="2026-10-03T12:00:00Z"), site(1), system="HIP 34457")
        done.first_seen = "2026-10-01T12:00:00Z"
        self.assertEqual(A.result_label(done), "Complete")
        self.assertEqual(A.took_text(done), "2.0 d")
        self.assertEqual(A.site_values(done)[1:], ("HIP 34457", "Complete", "2026-10-01", "2026-10-03", "2.0 d", "500 t"))
        text = A.summary_text(done)
        self.assertIn("Dolgov Depot (HIP 34457) - complete", text)
        self.assertIn("- Steel: 500 of 500 t", text)
        self.assertEqual(A.took_text(site(2, failed=True)), "")


if __name__ == "__main__":
    unittest.main()
