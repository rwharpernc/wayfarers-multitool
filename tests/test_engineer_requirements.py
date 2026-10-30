"""Checking an engineer's invitation requirement against the journal's ranks and lifetime figures (engineer_requirements.py): the events as the
game writes them, the numbers behind the table's words, keeping them per commander, and the note on the unlock path."""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from plugin import engineer_path as EP  # noqa: E402
from plugin import engineer_requirements as R  # noqa: E402
from plugin import engineers as E  # noqa: E402

# Shapes of real events (checked against real journals, 2026-10-30).
RANK = {"event": "Rank", "Combat": 3, "Trade": 12, "Explore": 8, "Soldier": 1, "Exobiologist": 6, "Empire": 0, "Federation": 8, "CQC": 0}
STATISTICS = {"timestamp": "2026-10-30T21:17:25Z", "event": "Statistics",
              "Exploration": {"Greatest_Distance_From_Start": 12345.678, "Total_Hyperspace_Jumps": 99},
              "Trading": {"Markets_Traded_With": 51}, "Smuggling": {"Black_Markets_Traded_With": 4},
              "Mining": {"Quantity_Mined": 612}, "Combat": {"Combat_Bonds": 50, "Bounties_Claimed": 16}}


def progress(*events):
    p = R.Progress()
    for e in events:
        p.apply_event(e)
    return p


class TableTests(unittest.TestCase):
    def test_every_check_is_for_an_engineer_in_the_table_and_agrees_with_their_words(self):
        for key, check in R.CHECKS.items():
            info = E.info(key)
            self.assertIsNotNone(info, key)
            if check.kind == "rank":
                self.assertIn(R.RANK_NAMES[check.key][check.value], info.invite, key)
            else:
                self.assertIn(f"{check.value:,}", info.invite, key)
                self.assertEqual(check.more_than, "more than" in info.invite.lower() or "over" in info.invite.lower(), key)

    def test_every_rank_check_names_a_rank_that_exists(self):
        for check in R.CHECKS.values():
            if check.kind == "rank":
                self.assertLess(check.value, len(R.RANK_NAMES[check.key]))
            else:
                self.assertIn(check.key, R.STAT_SOURCES)


class EventTests(unittest.TestCase):
    def test_rank_and_statistics_are_read(self):
        p = progress(RANK, STATISTICS)
        self.assertEqual(p.ranks["Combat"], 3)
        self.assertEqual(p.ranks["Trade"], 12)                  # Elite IV: the journal's numbers go past Elite (8) to Elite V (13)
        self.assertEqual(R.RANK_NAMES["Trade"][12], "Elite IV")
        self.assertEqual(p.stats["distance_from_start"], 12345)
        self.assertEqual(p.at, "2026-10-30T21:17:25Z")

    def test_a_promotion_changes_one_rank(self):
        p = progress(RANK)
        self.assertTrue(p.apply_event({"event": "Promotion", "Trade": 13}))
        self.assertEqual((p.ranks["Trade"], p.ranks["Combat"]), (13, 3))

    def test_an_event_that_changes_nothing_says_so(self):
        p = progress(RANK, STATISTICS)
        self.assertFalse(p.apply_event(RANK))
        self.assertFalse(p.apply_event(STATISTICS))
        self.assertFalse(p.apply_event({"event": "FSDJump"}))

    def test_odd_values_are_ignored(self):
        p = progress({"event": "Rank", "Combat": "high", "Trade": -1, "Explore": 99, "Empire": True},
                     {"event": "Statistics", "Trading": {"Markets_Traded_With": "many"}, "Mining": "none"})
        self.assertEqual((p.ranks, p.stats), ({}, {}))

    def test_it_survives_a_round_trip_and_a_damaged_file(self):
        p = progress(RANK, STATISTICS)
        self.assertEqual(R.Progress.from_json(p.to_json()), p)
        for junk in (None, "x", [], {"ranks": 5, "stats": "x", "at": 3}, {"ranks": {"Nope": 1, "Combat": "a"}}):
            self.assertEqual(R.Progress.from_json(junk), R.Progress())


class CheckTests(unittest.TestCase):
    def test_a_rank_is_met_at_or_above_the_one_asked_for(self):
        p = progress(RANK)
        self.assertTrue(p.check("broo tarquin").met)            # Competent asked, Competent held
        self.assertFalse(p.check("petra olmanova").met)         # Expert asked, Competent held
        self.assertEqual(p.check("petra olmanova").have, "Competent")
        self.assertTrue(p.check("etienne dorn").met)            # Trade 12 is above Dealer
        self.assertTrue(p.check("hera tani").met is False)      # no Empire rank (None)

    def test_more_than_means_more_than(self):
        p = progress(STATISTICS)
        self.assertTrue(p.check("lei cheung").met)              # 51 markets, more than 50
        self.assertFalse(p.check("juri ishmaak").met)           # exactly 50 bonds is not more than 50
        self.assertTrue(p.check("tod mcquinn").met)

    def test_at_least_means_at_least(self):
        p = progress(STATISTICS)
        self.assertTrue(p.check("selene jean").met)
        self.assertFalse(p.check("the dweller").met)            # 4 of 5
        self.assertTrue(p.check("chloe sedesi").met)
        self.assertEqual(p.check("chloe sedesi").have, "12,345 ly")

    def test_nothing_read_yet_is_unknown_not_unmet(self):
        self.assertIsNone(R.Progress().check("lei cheung").met)
        self.assertIn("not read from the game yet", R.Progress().check("lei cheung").describe())

    def test_a_requirement_the_journal_cannot_check_has_no_result(self):
        self.assertIsNone(progress(RANK, STATISTICS).check("marco qwent"))


class BookTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def book(self, cmdr="Bocheaux"):
        book = E.EngineerBook()
        book.load(self.tmp.name)
        book.set_commander(cmdr)
        return book

    def test_progress_is_kept_per_commander_and_across_restarts(self):
        book = self.book()
        self.assertTrue(book.apply_event(RANK))
        book.apply_event(STATISTICS)
        again = self.book()
        self.assertEqual(again.progress.ranks["Combat"], 3)
        self.assertEqual(again.progress.stats["markets_traded"], 51)
        self.assertEqual(self.book("Someone Else").progress, R.Progress())

    def test_a_listener_hears_of_a_promotion(self):
        book, heard = self.book(), []
        book.add_listener(lambda: heard.append(1))
        book.apply_event(RANK)
        self.assertEqual(heard, [1])
        book.apply_event(RANK)
        self.assertEqual(heard, [1])

    def test_the_standings_are_not_lost_when_progress_is_saved(self):
        book = self.book()
        book.apply_event({"event": "EngineerProgress", "Engineers": [{"Engineer": "Lei Cheung", "Progress": "Invited"}]})
        book.apply_event(RANK)
        self.assertEqual(self.book().standing("Lei Cheung").progress, E.INVITED)


class PathTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.book = E.EngineerBook()
        self.book.load(self.tmp.name)
        self.book.set_commander("Bocheaux")

    def invite(self, name):
        return [s for s in EP.build(name, self.book).steps if s.kind == EP.INVITE][0]

    def test_the_invitation_step_says_where_the_commander_stands(self):
        self.book.apply_event(RANK)
        self.assertEqual(self.invite("Petra Olmanova").note, "you have Competent: needs Expert")
        self.assertEqual(self.invite("Broo Tarquin").note, "you have Competent: met")
        self.assertIn("Competent: met", EP.render(EP.build("Broo Tarquin", self.book)))

    def test_a_note_never_marks_a_step_done(self):
        self.book.apply_event(RANK)
        self.assertFalse(self.invite("Broo Tarquin").done)

    def test_a_requirement_that_cannot_be_checked_has_no_note(self):
        self.assertEqual(self.invite("Marco Qwent").note, "")

    def test_without_a_book_there_is_no_note(self):
        step = [s for s in EP.build("Broo Tarquin").steps if s.kind == EP.INVITE][0]
        self.assertEqual(step.note, "")


class JournalScanTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.age = 0

    def journal(self, *events):
        """Write a journal file newer than the last one written."""
        self.age += 10
        path = os.path.join(self.tmp.name, f"Journal.2026-10-{self.age:02d}T000000.01.log")
        with open(path, "w", encoding="utf-8") as handle:
            for event in events:
                handle.write(json.dumps(event) + "\n")
        os.utime(path, (1_700_000_000 + self.age, 1_700_000_000 + self.age))

    def read(self, cmdr="Bocheaux"):
        return R.read_from_journals(cmdr, self.tmp.name)

    def test_the_newest_rank_and_statistics_are_found(self):
        self.journal({"event": "Commander", "Name": "Bocheaux"}, dict(RANK, Combat=1), dict(STATISTICS, Trading={"Markets_Traded_With": 10}))
        self.journal({"event": "Commander", "Name": "Bocheaux"}, RANK, STATISTICS)
        found = self.read()
        self.assertEqual((found.ranks["Combat"], found.stats["markets_traded"]), (3, 51))

    def test_a_promotion_since_the_login_is_applied(self):
        self.journal({"event": "Commander", "Name": "Bocheaux"}, RANK, STATISTICS, {"event": "Promotion", "Combat": 4})
        self.assertEqual(self.read().ranks["Combat"], 4)

    def test_another_commanders_events_are_ignored(self):
        self.journal({"event": "Commander", "Name": "Someone"}, dict(RANK, Combat=8), {"event": "Commander", "Name": "Bocheaux"}, RANK)
        self.assertEqual(self.read().ranks["Combat"], 3)
        self.assertTrue(self.read("Nobody").empty)

    def test_an_older_file_supplies_what_the_newest_lacks(self):
        self.journal({"event": "Commander", "Name": "Bocheaux"}, RANK, STATISTICS)
        self.journal({"event": "LoadGame", "Commander": "Bocheaux"}, {"event": "Promotion", "Explore": 9})     # a session started after the login
        found = self.read()
        self.assertEqual((found.ranks["Explore"], found.ranks["Combat"], found.stats["markets_traded"]), (9, 3, 51))

    def test_no_journals_or_no_commander_gives_nothing(self):
        self.assertTrue(self.read().empty)
        self.assertTrue(R.read_from_journals("", self.tmp.name).empty)
        self.assertTrue(R.read_from_journals("Bocheaux", os.path.join(self.tmp.name, "missing")).empty)


class FillTests(unittest.TestCase):
    def test_what_is_there_is_kept_and_only_gaps_are_filled(self):
        live = progress({"event": "Promotion", "Combat": 5})
        self.assertTrue(live.fill_from(progress(RANK, STATISTICS)))
        self.assertEqual((live.ranks["Combat"], live.ranks["Trade"], live.stats["markets_traded"]), (5, 12, 51))
        self.assertFalse(live.fill_from(progress(RANK, STATISTICS)))

    def test_the_book_adopts_for_the_right_commander_only(self):
        with tempfile.TemporaryDirectory() as folder:
            book = E.EngineerBook()
            book.load(folder)
            self.assertFalse(book.needs_journal_read())              # no commander yet
            book.set_commander("Bocheaux")
            self.assertTrue(book.needs_journal_read())
            self.assertFalse(book.adopt_progress("Someone Else", progress(RANK)))
            self.assertTrue(book.adopt_progress("bocheaux", progress(RANK, STATISTICS)))
            self.assertFalse(book.needs_journal_read())
            again = E.EngineerBook()
            again.load(folder)
            again.set_commander("Bocheaux")
            self.assertEqual(again.progress.ranks["Combat"], 3)


if __name__ == "__main__":
    unittest.main()
