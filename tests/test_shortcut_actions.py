"""The shortcut list, its chat commands and the check against Elite's own key bindings (plugin/shortcut_actions.py, plugin/elite_keybinds.py). Pure logic."""

import os
import sys
import unittest
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from plugin import elite_keybinds as binds  # noqa: E402
from plugin import shortcut_actions as actions  # noqa: E402

_BINDS = """<?xml version="1.0" encoding="UTF-8" ?>
<Root>
  <FireChaffLauncher>
    <Primary Device="Keyboard" Key="Key_C">
      <Modifier Device="Keyboard" Key="Key_LeftControl" />
    </Primary>
    <Secondary Device="{NoDevice}" Key="" />
  </FireChaffLauncher>
  <Dummy>
    <Primary Device="Keyboard" Key="Key_C">
      <Modifier Device="Keyboard" Key="Key_LeftControl" />
      <Modifier Device="Keyboard" Key="Key_RightAlt" />
      <Modifier Device="Keyboard" Key="Key_LeftShift" />
    </Primary>
    <Secondary Device="Keyboard" Key="Key_F9" />
  </Dummy>
  <HotasOnly><Primary Device="231D0200" Key="Joy_1" /></HotasOnly>
  <Plain><Primary Device="Keyboard" Key="Key_5" /></Plain>
</Root>
"""


class ActionTests(unittest.TestCase):
    def test_every_key_is_unique_by_default(self) -> None:
        self.assertEqual(actions.duplicate_keys(actions.default_keys()), {})

    def test_every_action_has_a_chat_word_and_a_default_that_is_a_choice(self) -> None:
        words = [a.word for a in actions.ACTIONS]
        self.assertEqual(len(words), len(set(words)))
        for a in actions.ACTIONS:
            self.assertIn(a.default_key, actions.KEY_CHOICES)
            self.assertIs(actions.parse_chat(f"!wf {a.word}"), a)

    def test_the_combination_is_the_same_modifiers_for_every_key(self) -> None:
        self.assertEqual(actions.combo_text("C"), "Ctrl+Alt+Shift+C")
        self.assertEqual(actions.combo_text("F9"), "Ctrl+Alt+Shift+F9")
        self.assertEqual(actions.combo_text(actions.OFF), "Off")

    def test_function_keys_and_digits_are_offered(self) -> None:
        self.assertIn("F12", actions.KEY_CHOICES)
        self.assertIn("7", actions.KEY_CHOICES)
        self.assertNotIn("F13", actions.KEY_CHOICES)

    def test_a_saved_key_that_is_not_a_choice_falls_back(self) -> None:
        self.assertEqual(actions.clean_key("", "C"), "C")
        self.assertEqual(actions.clean_key("Ctrl+Alt+H", "H"), "H")
        self.assertEqual(actions.clean_key("F9", "C"), "F9")
        self.assertEqual(actions.clean_key("Off", "C"), "Off")

    def test_duplicates_are_found_but_off_is_not_one(self) -> None:
        self.assertEqual(actions.duplicate_keys({"center": "C", "border": "C", "zoom": "Off", "live": "Off"}), {"C": ("center", "border")})

    def test_chat_commands(self) -> None:
        self.assertEqual(actions.parse_chat("!wf center").id, "center")
        self.assertEqual(actions.parse_chat("  !WF  Border ").id, "border")
        for message in ("!wf", "!wf center now", "wf center", "hello !wf center", "!wfx center", "!wf unknown", "", None, 5):
            self.assertIsNone(actions.parse_chat(message), repr(message))


class WindowsKeyTests(unittest.TestCase):
    def test_letters_digits_and_function_keys_map_to_virtual_keys(self) -> None:
        mods = actions.MOD_CONTROL | actions.MOD_ALT | actions.MOD_SHIFT
        self.assertEqual(actions.win_hotkey("C"), (mods, ord("C")))
        self.assertEqual(actions.win_hotkey("5"), (mods, ord("5")))
        self.assertEqual(actions.win_hotkey("F1"), (mods, 0x70))
        self.assertEqual(actions.win_hotkey("F10"), (mods, 0x79))
        self.assertEqual(actions.win_hotkey("F12"), (mods, 0x7B))

    def test_off_and_anything_else_is_none(self) -> None:
        for text in ("Off", "", "c", "Home", "F13", "Ctrl+C"):
            self.assertIsNone(actions.win_hotkey(text), text)

    def test_every_choice_but_off_is_a_valid_key(self) -> None:
        for choice in actions.KEY_CHOICES:
            self.assertEqual(actions.win_hotkey(choice) is None, choice == actions.OFF, choice)


class FreshnessTests(unittest.TestCase):
    NOW = datetime(2026, 10, 20, 12, 0, 0, tzinfo=timezone.utc)

    def test_a_command_just_typed_is_recent_and_an_old_one_is_not(self) -> None:
        self.assertTrue(actions.is_recent("2026-10-20T11:59:50Z", self.NOW, 30.0))
        self.assertTrue(actions.is_recent("2026-10-20T12:00:00Z", self.NOW, 30.0))
        self.assertFalse(actions.is_recent("2026-10-20T11:59:00Z", self.NOW, 30.0), "a minute old: from before EDMC started or a replay")
        self.assertFalse(actions.is_recent("2026-10-19T12:00:00Z", self.NOW, 30.0))

    def test_a_small_clock_difference_is_allowed_and_a_big_one_is_not(self) -> None:
        self.assertTrue(actions.is_recent("2026-10-20T12:00:20Z", self.NOW, 30.0))
        self.assertFalse(actions.is_recent("2026-10-20T13:00:00Z", self.NOW, 30.0))

    def test_anything_unreadable_is_not_recent(self) -> None:
        for value in (None, "", "yesterday", 5, "2026-10-20 12:00:00"):
            self.assertFalse(actions.is_recent(value, self.NOW, 30.0), repr(value))


class ConflictTextTests(unittest.TestCase):
    def setUp(self) -> None:
        self.bindings = binds.parse(_BINDS)

    def test_no_clash_gives_no_text(self) -> None:
        self.assertEqual(actions.conflict_text("B", {"center": "C", "border": "B"}, "border", self.bindings), "")
        self.assertEqual(actions.conflict_text(actions.OFF, {"center": "Off"}, "center", self.bindings), "")

    def test_another_wfmt_action_on_the_key_is_named(self) -> None:
        text = actions.conflict_text("C", {"center": "C", "border": "C"}, "center", None)
        self.assertIn("Mark the border", text)

    def test_an_elite_control_on_exactly_that_combination_is_named(self) -> None:
        text = actions.conflict_text("C", {"center": "C"}, "center", self.bindings)
        self.assertIn("Dummy", text)
        self.assertIn("Ctrl+Alt+Shift+C", text)

    def test_with_no_bindings_file_only_wfmt_clashes_are_reported(self) -> None:
        self.assertEqual(actions.conflict_text("C", {"center": "C"}, "center", None), "")


class KeybindsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.parsed = binds.parse(_BINDS)

    def test_keyboard_bindings_are_read_with_their_modifiers(self) -> None:
        self.assertIn(binds.Binding("FireChaffLauncher", "C", frozenset({binds.CTRL})), self.parsed)
        self.assertIn(binds.Binding("Dummy", "C", frozenset({binds.CTRL, binds.ALT, binds.SHIFT})), self.parsed)
        self.assertIn(binds.Binding("Dummy", "F9", frozenset()), self.parsed)
        self.assertIn(binds.Binding("Plain", "5", frozenset()), self.parsed)

    def test_other_devices_and_empty_slots_are_ignored(self) -> None:
        self.assertFalse([b for b in self.parsed if b.action == "HotasOnly"])
        self.assertEqual(len([b for b in self.parsed if b.action == "FireChaffLauncher"]), 1)

    def test_a_clash_needs_the_same_key_and_the_same_modifiers(self) -> None:
        triple = frozenset({binds.CTRL, binds.ALT, binds.SHIFT})
        self.assertEqual(binds.clashes(self.parsed, "C", triple), ["Dummy"])
        self.assertEqual(binds.clashes(self.parsed, "B", triple), [])
        self.assertEqual(binds.clashes(self.parsed, "F9", triple), [], "the same key with fewer modifiers is not a clash")
        self.assertEqual(binds.same_key_elsewhere(self.parsed, "F9", triple), ["Dummy"])

    def test_left_and_right_modifiers_count_alike(self) -> None:
        self.assertEqual(next(b for b in self.parsed if b.action == "Dummy" and b.key == "C").modifiers, frozenset({binds.CTRL, binds.ALT, binds.SHIFT}))

    def test_a_file_that_is_not_xml_gives_nothing(self) -> None:
        self.assertEqual(binds.parse("not xml <"), [])
        self.assertEqual(binds.parse(""), [])

    def test_load_says_none_when_there_is_no_file(self) -> None:
        self.assertIsNone(binds.load(lambda: None))
        self.assertEqual(binds.load(lambda: _BINDS), self.parsed)


if __name__ == "__main__":
    unittest.main()
