"""The path to unlocking an engineer (engineer_path.py): the engineers to deal with first, the steps in order, and what is marked done."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from plugin import engineer_path as EP  # noqa: E402
from plugin import engineers as E  # noqa: E402


def book_with(folder, *entries):
    book = E.EngineerBook()
    book.load(folder)
    book.set_commander("Bocheaux")
    book.apply_event({"event": "EngineerProgress", "Engineers": [
        {"Engineer": name, "EngineerID": 1, "Progress": progress, **({"Rank": 3, "RankProgress": 0} if progress == "Unlocked" else {})}
        for name, progress in entries]})
    return book


class PrerequisiteTests(unittest.TestCase):
    def test_a_referral_names_the_engineer_to_deal_with_first(self):
        self.assertEqual(EP.prerequisites("Hera Tani"), ["Liz Ryder"])
        self.assertEqual(EP.prerequisites("Tiana Fortune"), ["Hera Tani"])

    def test_the_colonia_referral_tasks_name_all_three(self):
        self.assertEqual(sorted(EP.prerequisites("Yi Shen")), ["Baltanos", "Eleanor Bresa", "Rosa Dayette"])

    def test_an_engineer_open_to_everyone_needs_nobody_first(self):
        self.assertEqual(EP.prerequisites("Felicity Farseer"), [])
        self.assertEqual(EP.prerequisites("Not An Engineer"), [])

    def test_no_engineer_is_their_own_prerequisite_and_no_chain_loops(self):
        for info in E.INFO.values():
            self.assertNotIn(info.name, EP.prerequisites(info.name))
            path = EP.build(info.name)
            names = [p.name for p in EP.order(path)]
            self.assertEqual(len(names), len(set(names)), info.name)
            self.assertEqual(names[-1], info.name)

    def test_a_nickname_in_the_journal_still_finds_the_table_entry(self):
        self.assertEqual(EP.prerequisites("Tod 'The Blaster' McQuinn"), [])
        self.assertEqual(EP.prerequisites("Selene Jean"), ["Tod 'The Blaster' McQuinn"])


class BuildTests(unittest.TestCase):
    def test_the_steps_run_find_then_invite_then_unlock(self):
        path = EP.build("Lei Cheung")
        self.assertEqual([s.kind for s in path.steps], [EP.FIND, EP.INVITE, EP.UNLOCK])
        self.assertFalse(any(s.done for s in path.steps))
        self.assertEqual(path.next_step.kind, EP.FIND)

    def test_a_permit_adds_a_step_to_reach_them(self):
        kinds = [s.kind for s in EP.build("Bill Turner").steps]
        self.assertIn(EP.REACH, kinds)
        self.assertNotIn(EP.REACH, [s.kind for s in EP.build("Felicity Farseer").steps])

    def test_an_engineer_with_nothing_to_unlock_has_no_unlock_step(self):
        self.assertNotIn(EP.UNLOCK, [s.kind for s in EP.build("Yi Shen").steps])

    def test_an_unknown_engineer_has_no_path(self):
        self.assertIsNone(EP.build("Not An Engineer"))


class StandingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def done(self, path):
        return [s.kind for s in path.steps if s.done]

    def test_known_means_found(self):
        book = book_with(self.tmp.name, ("Lei Cheung", "Known"))
        path = EP.build("Lei Cheung", book)
        self.assertEqual(self.done(path), [EP.FIND])
        self.assertEqual(path.next_step.kind, EP.INVITE)

    def test_invited_means_found_and_invited(self):
        book = book_with(self.tmp.name, ("Lei Cheung", "Invited"))
        path = EP.build("Lei Cheung", book)
        self.assertEqual(self.done(path), [EP.FIND, EP.INVITE])
        self.assertEqual(path.next_step.kind, EP.UNLOCK)

    def test_unlocked_means_everything_is_done_and_nobody_is_needed_first(self):
        book = book_with(self.tmp.name, ("Tiana Fortune", "Unlocked"))
        path = EP.build("Tiana Fortune", book)
        self.assertTrue(path.unlocked)
        self.assertIsNone(path.next_step)
        self.assertEqual(path.first, ())
        self.assertIn("Nothing left to do", EP.render(path))

    def test_a_permit_is_not_done_until_the_engineer_is_unlocked(self):
        book = book_with(self.tmp.name, ("Bill Turner", "Invited"))
        reach = [s for s in EP.build("Bill Turner", book).steps if s.kind == EP.REACH][0]
        self.assertFalse(reach.done)

    def test_the_nickname_in_the_journal_matches(self):
        book = book_with(self.tmp.name, ("Tod 'The Blaster' McQuinn", "Unlocked"))
        self.assertTrue(EP.build("Tod McQuinn", book).unlocked)


class OrderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def names(self, path):
        return [p.name for p in EP.order(path)]

    def test_the_chain_runs_from_the_root_to_the_engineer_asked_about(self):
        self.assertEqual(self.names(EP.build("Tiana Fortune")), ["Liz Ryder", "Hera Tani", "Tiana Fortune"])

    def test_an_engineer_already_unlocked_on_the_way_is_left_out(self):
        book = book_with(self.tmp.name, ("Liz Ryder", "Unlocked"))
        self.assertEqual(self.names(EP.build("Tiana Fortune", book)), ["Hera Tani", "Tiana Fortune"])

    def test_the_text_lists_the_order_and_marks_what_is_done(self):
        book = book_with(self.tmp.name, ("Liz Ryder", "Unlocked"), ("Hera Tani", "Invited"))
        text = EP.render(EP.build("Tiana Fortune", book))
        self.assertIn("Hera Tani", text)
        self.assertNotIn("Liz Ryder:", text)
        self.assertIn("[done]", text)
        self.assertIn("Tiana Fortune:", text)

    def test_a_single_engineer_has_no_order_line(self):
        self.assertNotIn("takes", EP.render(EP.build("Felicity Farseer")))
        self.assertIn("takes 3 engineers", EP.render(EP.build("Tiana Fortune")))


if __name__ == "__main__":
    unittest.main()
