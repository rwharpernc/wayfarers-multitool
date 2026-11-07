"""The ranks table (ranks.py): the game's names for every ladder, the percent toward the next rank, and keeping one commander's figures apart from
another's. The events are shaped as the game writes them (checked against real journals, 2026-11-07)."""
from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from plugin import engineer_requirements as ER  # noqa: E402
from plugin import ranks  # noqa: E402

RANK = {"event": "Rank", "Combat": 4, "Trade": 13, "Explore": 8, "Soldier": 2, "Exobiologist": 7, "Empire": 12, "Federation": 11, "CQC": 0}
PROGRESS = {"event": "Progress", "Combat": 99, "Trade": 100, "Explore": 98, "Soldier": 94, "Exobiologist": 98, "Empire": 100, "Federation": 100, "CQC": 0}


def book(*events, cmdr="Mactavious"):
    held = ranks.RankBook()
    for event in events:
        held.take(event, cmdr)
    return held


class LadderTests(unittest.TestCase):
    def test_every_pilots_federation_ladder_has_fourteen_ranks_and_each_navy_fifteen(self) -> None:
        for key in ("Combat", "Trade", "Explore", "CQC", "Soldier", "Exobiologist"):
            self.assertEqual(len(ranks.names(key)), 14, key)
            self.assertEqual(ranks.names(key)[8:], ("Elite",) + ranks.ELITE_TIERS, key)
        for key in ("Federation", "Empire"):
            self.assertEqual(len(ranks.names(key)), 15, key)

    def test_the_names_are_the_games(self) -> None:
        self.assertEqual(ranks.rank_name("Combat", 0), "Harmless")
        self.assertEqual(ranks.rank_name("Trade", 13), "Elite V")
        self.assertEqual(ranks.rank_name("Explore", 4), "Trailblazer")           # the journal reference says Explorer; the game shows Trailblazer
        self.assertEqual(ranks.rank_name("CQC", 3), "Semi Professional")
        self.assertEqual(ranks.rank_name("Soldier", 0), "Defenceless")   # game spelling
        self.assertEqual(ranks.rank_name("Exobiologist", 7), "Geneticist")
        self.assertEqual(ranks.rank_name("Federation", 9), "Lieutenant Commander")
        self.assertEqual(ranks.rank_name("Empire", 14), "King")

    def test_a_rank_past_the_end_is_reported_not_guessed(self) -> None:
        self.assertEqual(ranks.rank_name("Combat", 14), "Rank 14")
        self.assertEqual(ranks.rank_name("Federation", -1), "Rank -1")
        self.assertEqual(ranks.rank_name("Nonsense", 2), "Rank 2")

    def test_a_rank_past_the_end_is_not_the_top_and_keeps_its_percent(self) -> None:
        self.assertFalse(ranks.is_top("Federation", 15))
        self.assertFalse(ranks.is_top("Combat", 14))
        rows = book({"event": "Rank", "Federation": 15}, {"event": "Progress", "Federation": 30}).rows()
        self.assertEqual(rows, [("Federation", "Rank 15", "30%")])

    def test_the_strict_table_fails_on_an_unknown_ladder(self) -> None:
        self.assertEqual(set(ranks.NAMES), set(ranks.KEYS))
        with self.assertRaises(KeyError):
            ranks.NAMES["Exploration"]      # the journal's key is Explore; a misspelling must not become an empty ladder

    def test_the_last_rank_of_a_ladder_is_the_top(self) -> None:
        self.assertTrue(ranks.is_top("Trade", 13))
        self.assertFalse(ranks.is_top("Trade", 12))
        self.assertTrue(ranks.is_top("Empire", 14))
        self.assertFalse(ranks.is_top("Nonsense", 0))

    def test_the_engineer_requirements_use_the_same_names(self) -> None:
        for key, names in ER.RANK_NAMES.items():
            self.assertEqual(names, ranks.names(key), key)


class PercentTests(unittest.TestCase):
    def test_progress_is_kept_within_zero_to_one_hundred(self) -> None:
        self.assertEqual([ranks.percent(v) for v in (0, 57, 100, 130, -4)], [0, 57, 100, 100, 0])

    def test_something_that_is_not_a_number_is_zero(self) -> None:
        self.assertEqual([ranks.percent(v) for v in (None, "40", True, float("nan"), float("inf"))], [0, 0, 0, 0, 0])

    def test_a_fractional_progress_is_rounded_not_dropped(self) -> None:
        self.assertEqual([ranks.percent(v) for v in (45.4, 45.6, 99.7, -0.2)], [45, 46, 100, 0])
        held = book({"event": "Rank", "Combat": 2}, {"event": "Progress", "Combat": 45.6})
        self.assertEqual(held.rows(), [("Combat", "Novice", "46%")])

    def test_a_non_finite_number_in_an_event_is_ignored_without_an_error(self) -> None:
        held = book({"event": "Rank", "Combat": float("inf"), "Trade": float("nan"), "Explore": 3},
                    {"event": "Progress", "Explore": float("inf"), "Combat": 10})
        self.assertEqual([r[0] for r in held.rows()], ["Exploration"])
        self.assertEqual(ranks.values_from_entry({"Combat": float("inf")}, whole=False), {})


class TableTests(unittest.TestCase):
    def test_every_ladder_is_listed_with_its_name_and_percent(self) -> None:
        rows = book(RANK, PROGRESS).rows()
        self.assertEqual([r[0] for r in rows], ["Combat", "Trade", "Exploration", "CQC", "Mercenary", "Exobiologist", "Federation", "Empire"])
        by_label = {r[0]: r[1:] for r in rows}
        self.assertEqual(by_label["Combat"], ("Expert", "99%"))
        self.assertEqual(by_label["Exploration"], ("Elite", "98%"))
        self.assertEqual(by_label["Mercenary"], ("Rookie", "94%"))
        self.assertEqual(by_label["CQC"], ("Helpless", "0%"))
        self.assertEqual(by_label["Federation"], ("Post Captain", "100%"))

    def test_the_top_rank_reads_max(self) -> None:
        self.assertEqual({r[0]: r[2] for r in book(RANK, PROGRESS).rows()}["Trade"], "max")
        self.assertEqual({r[0]: r[2] for r in book({"event": "Rank", "Empire": 14}).rows()}["Empire"], "max")

    def test_a_ladder_with_no_rank_is_left_out_and_a_rank_with_no_progress_reads_zero(self) -> None:
        rows = book({"event": "Rank", "Combat": 2}).rows()
        self.assertEqual(rows, [("Combat", "Novice", "0%")])

    def test_nothing_is_listed_before_the_game_reports(self) -> None:
        self.assertEqual(ranks.RankBook().rows(), [])
        self.assertEqual(list(ranks.missing({"Combat": 1})), [k for k in ranks.KEYS if k != "Combat"])


class RankBookTests(unittest.TestCase):
    def test_progress_updates_in_place(self) -> None:
        held = book(RANK, PROGRESS)
        self.assertTrue(held.take({"event": "Progress", "Combat": 12}, "Mactavious"))
        self.assertEqual({r[0]: r[2] for r in held.rows()}["Combat"], "12%")

    def test_a_promotion_sets_the_rank_and_starts_it_at_zero(self) -> None:
        held = book(RANK, PROGRESS)
        held.take({"event": "Promotion", "Combat": 5}, "Mactavious")
        self.assertEqual({r[0]: r[1:] for r in held.rows()}["Combat"], ("Master", "0%"))

    def test_an_event_that_changes_nothing_says_so(self) -> None:
        held = book(RANK, PROGRESS)
        self.assertFalse(held.take(PROGRESS, "Mactavious"))
        self.assertFalse(held.take({"event": "FSDJump"}, "Mactavious"))

    def test_a_different_commander_starts_empty(self) -> None:
        held = book(RANK, PROGRESS, cmdr="Mactavious")
        held.take({"event": "LoadGame"}, "Someone Else", {"Rank": {"Combat": (8, 50)}})
        self.assertEqual(held.rows(), [], "nothing of the last commander's, and no state until that commander's own events arrive")
        held.take({"event": "Rank", "Combat": 1}, "Someone Else")
        self.assertEqual(held.rows(), [("Combat", "Mostly Harmless", "0%")])

    def test_edmcs_state_fills_in_when_the_game_was_already_running(self) -> None:
        state = {"Rank": {"Combat": (3, 40), "Trade": (13, 0), "Explore": None, "Federation": [9, 61]}}
        held = ranks.RankBook()
        held.take({"event": "FSDJump"}, "Mactavious", state)
        self.assertEqual(held.rows(), [("Combat", "Competent", "40%"), ("Trade", "Elite V", "max"), ("Federation", "Lieutenant Commander", "61%")])

    def test_a_promotion_first_does_not_switch_off_edmcs_state(self) -> None:
        state = {"Rank": {"Combat": (3, 40), "Trade": (5, 10)}}
        held = ranks.RankBook()
        held.take({"event": "Promotion", "Combat": 4}, "Mactavious", state)
        self.assertEqual(held.rows(), [("Combat", "Expert", "0%"), ("Trade", "Broker", "10%")])

    def test_edmcs_state_is_read_once_per_commander(self) -> None:
        held = ranks.RankBook()
        held.take({"event": "FSDJump"}, "Mactavious", {"Rank": {"Combat": (3, 40)}})
        held.take({"event": "FSDJump"}, "Mactavious", {"Rank": {"Combat": (9, 99), "Trade": (2, 2)}})
        self.assertEqual(held.rows(), [("Combat", "Competent", "40%")], "a later state does not overwrite or add to what was seeded")

    def test_the_last_commanders_state_is_never_shown_on_the_next(self) -> None:
        stale = {"Rank": {"Combat": (8, 50)}}
        held = book(RANK, PROGRESS, cmdr="Mactavious")
        held.take({"event": "LoadGame"}, "Someone Else", stale)
        held.take({"event": "FSDJump"}, "Someone Else", stale)       # the next event, before the game's own Rank
        held.take({"event": "Cargo"}, "Someone Else", stale)
        self.assertEqual(held.rows(), [])
        held.take({"event": "Rank", "Combat": 1}, "Someone Else", stale)
        self.assertEqual(held.rows(), [("Combat", "Mostly Harmless", "0%")])

    def test_events_before_a_commander_is_known_do_not_use_up_the_state(self) -> None:
        held = ranks.RankBook()
        self.assertFalse(held.take({"event": "Fileheader"}, "", {"Rank": {"Combat": (3, 40)}}))
        self.assertEqual(held.rows(), [])
        held.take({"event": "LoadGame"}, "Mactavious", {"Rank": {"Combat": (3, 40)}})
        self.assertEqual(held.rows(), [("Combat", "Competent", "40%")])

    def test_odd_values_are_ignored(self) -> None:
        held = book({"event": "Rank", "Combat": "4", "Trade": True, "Explore": 3, "Empire": 2.0})
        self.assertEqual([r[0] for r in held.rows()], ["Exploration", "Empire"])
        self.assertEqual(ranks.values_from_state({"Rank": "no"}), ({}, {}))
        self.assertEqual(ranks.values_from_state(None), ({}, {}))


if __name__ == "__main__":
    unittest.main()
