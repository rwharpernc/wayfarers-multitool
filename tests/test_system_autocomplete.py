"""Type-ahead for system-name boxes (system_autocomplete.py): the list under a real Tk box as you type, taking a suggestion with the keys, Enter
passing on to the box's own handler when nothing is highlighted, and Spansh's suggestions arriving after a pause. Skipped when Tk has no display."""
from __future__ import annotations

import os
import sys
import time
import types
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

if "config" not in sys.modules:
    _stub = types.ModuleType("config")
    _stub.appname = "EDMarketConnector"  # type: ignore[attr-defined]
    _stub.config = types.SimpleNamespace(get_bool=lambda key, default=False: False, get_str=lambda *_a, **_k: "", default_journal_dir="")
    sys.modules["config"] = _stub

import tkinter as tk  # noqa: E402

from plugin import system_autocomplete as A  # noqa: E402
from plugin import system_names as N  # noqa: E402

SETTINGS = {}


class AutocompleteTests(unittest.TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tk has no display here")
        self.root.geometry("400x200+50+50")
        N.clear()
        SETTINGS.clear()
        for module in (N, A.online_lookups):          # the box and the warning's wording each read the saved switch
            patch = mock.patch.object(module, "config", types.SimpleNamespace(get_bool=lambda key, default=False: SETTINGS.get(key, default)))
            patch.start()
            self.addCleanup(patch.stop)
        self.var = tk.StringVar()
        self.entry = tk.Entry(self.root, textvariable=self.var, width=30)
        self.entry.pack()
        self.submitted = []
        self.entry.bind("<Return>", lambda _e: self.submitted.append(self.var.get()))
        self.picked = []
        self.box = A.attach(self.entry, self.var, on_pick=lambda: self.picked.append(self.var.get()))
        self.root.update()
        self.entry.focus_force()
        self.root.update()
        self.addCleanup(self.root.destroy)

    def type(self, text):
        self.var.set(text)
        self.entry.icursor("end")
        self.entry.event_generate("<KeyRelease>", keysym="x")
        self.root.update()

    def key(self, name):
        self.entry.event_generate(f"<{name}>")
        self.root.update()

    def shown(self):
        return list(self.box._listbox.get(0, "end")) if self.box._listbox is not None else []

    def test_known_systems_are_suggested_from_two_letters_best_matches_first(self):
        for name in ("Sol", "Colonia", "Solitude", "Beagle Point"):
            N.remember(name)
        self.type("s")
        self.assertEqual(self.shown(), [])
        self.type("so")
        self.assertEqual(self.shown(), ["Solitude", "Sol"])           # most recent first, both start with it
        self.type("point")
        self.assertEqual(self.shown(), ["Beagle Point"])               # a name that merely contains it still comes up

    def test_the_systems_in_the_journals_are_suggested_after_the_sessions_own(self):
        N.set_visited(["Sol", "Solitude", "Solar Plexus"])
        N.remember("Soho")
        self.type("so")
        self.assertEqual(self.shown(), ["Soho", "Sol", "Solar Plexus", "Solitude"])

    def test_with_spansh_off_a_system_that_is_nowhere_says_where_to_turn_it_on(self):
        N.set_visited(["Sol"])
        self.type("colon")
        self.assertIsNone(self.box._listbox, "there is no list to take from")
        self.assertIsNotNone(self.box._popup, "the hint is up")
        self.assertIn("Spansh", A.hint_text())
        self.assertIn("Settings > Online", A.hint_text())

    def test_no_hint_for_a_system_that_is_known_one_that_is_too_short_or_with_spansh_on(self):
        N.set_visited(["Sol"])
        self.type("Sol")                                   # typed in full: found, so nothing to explain
        self.assertIsNone(self.box._popup)
        self.type("sol")                                   # other capitals: the list offers the right spelling, not a hint
        self.assertEqual(self.shown(), ["Sol"])
        self.type("co")                                    # too short to look anything up
        self.assertIsNone(self.box._popup)
        SETTINGS[N.CFG_REMOTE] = True
        self.type("colonx")                                # the lookup is on, so no hint (the answer arrives on its own)
        self.assertIsNone(self.box._popup)

    def test_the_hint_gives_way_to_a_list_and_a_list_to_the_hint(self):
        N.set_visited(["Colonia"])
        self.type("colx")
        self.assertIsNotNone(self.box._popup)
        self.type("colo")
        self.assertEqual(self.shown(), ["Colonia"])
        self.type("coloz")
        self.assertIsNone(self.box._listbox)
        self.assertIsNotNone(self.box._popup)

    def test_down_and_enter_take_a_suggestion_and_do_not_also_run_the_boxs_own_enter(self):
        N.remember("Sol")
        N.remember("Solitude")
        self.type("sol")
        self.key("Down")
        self.key("Return")
        self.assertEqual(self.var.get(), "Solitude")
        self.assertEqual(self.picked, ["Solitude"])
        self.assertEqual(self.submitted, [])
        self.assertIsNone(self.box._listbox)

    def test_enter_with_nothing_highlighted_goes_on_to_the_boxs_own_handler(self):
        N.remember("Solitude")
        self.type("sol")
        self.assertEqual(self.shown(), ["Solitude"])
        self.key("Return")
        self.assertEqual(self.submitted, ["sol"])
        self.assertEqual(self.var.get(), "sol")
        self.assertIsNone(self.box._listbox)

    def test_escape_closes_the_list_and_a_second_escape_is_left_alone(self):
        N.remember("Solitude")
        self.type("sol")
        self.assertTrue(self.shown())
        self.key("Escape")
        self.assertIsNone(self.box._listbox)

    def test_a_name_already_typed_in_full_is_not_offered_again(self):
        N.remember("Sol")
        self.type("Sol")
        self.assertEqual(self.shown(), [])

    def test_spansh_suggestions_arrive_after_a_pause_only_when_switched_on(self):
        N.remember("Sol")
        asked = []

        def fetch(text):
            asked.append(text)
            N._cache[N.key(text)] = ["Solitude", "Sollaro"]
            return ["Solitude", "Sollaro"]

        with mock.patch.object(N, "fetch", side_effect=fetch):
            self.type("sol")
            time.sleep(A.DEBOUNCE_MS / 1000 + 0.2)
            self.root.update()
            self.assertEqual(asked, [])                                  # switched off: nothing asked
            SETTINGS[N.CFG_REMOTE] = True
            self.type("sol")
            for _ in range(40):
                self.root.update()
                if asked:
                    break
                time.sleep(0.05)
            for _ in range(20):
                self.root.update()
                time.sleep(0.05)
        self.assertEqual(asked, ["sol"])
        self.assertEqual(self.shown(), ["Sol", "Solitude", "Sollaro"])


if __name__ == "__main__":
    unittest.main()
