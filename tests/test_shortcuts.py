"""The shortcuts runtime (plugin/shortcuts.py): chat commands from the journal, what each action calls, and what is saved. No Tk window and no EDMC; the pure parts are tested in
test_shortcut_actions.py."""

import os
import sys
import types
import unittest
from datetime import datetime, timedelta, timezone
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

_saved = {}
_config = types.ModuleType("config")
_config.appname = "EDMarketConnector"
_config.user_agent = "WFMT-test"
_config.appversion = lambda: "5.13.0"
_config.config = types.SimpleNamespace(
    get_str=lambda key, default="": _saved.get(key, default),
    get_bool=lambda key, default=False: _saved.get(key, default),
    get_int=lambda key, default=0: _saved.get(key, default),
    set=lambda key, value: _saved.__setitem__(key, value))
sys.modules["config"] = _config


class _Any(types.ModuleType):
    """A stand-in for an EDMC module: any attribute is a mock."""

    def __getattr__(self, name):
        if name.startswith("__"):
            raise AttributeError(name)
        return mock.MagicMock()


for _name in ("monitor", "plug", "EDMCLogging", "l10n", "killswitch", "requests", "win32api", "win32con", "win32gui", "win32process", "win32clipboard", "pywintypes",
              "psutil", "ttkHyperlinkLabel", "theme", "myNotebook"):
    sys.modules.setdefault(_name, _Any(_name))

from plugin import mining_live_window  # noqa: E402
from plugin import overlay  # noqa: E402
from plugin import platform_support  # noqa: E402
from plugin import shortcut_actions as actions  # noqa: E402
from plugin import shortcuts  # noqa: E402


def _stamp(seconds_ago: float) -> str:
    return (datetime.now(timezone.utc) - timedelta(seconds=seconds_ago)).strftime("%Y-%m-%dT%H:%M:%SZ")


def _chat(message: str, seconds_ago: float = 1.0) -> dict:
    return {"timestamp": _stamp(seconds_ago), "event": "SendText", "To": "local", "Message": message}


class ChatCommandTests(unittest.TestCase):
    def setUp(self) -> None:
        _saved.clear()
        shortcuts._tk_widget = None
        patcher = mock.patch.object(shortcuts, "run")
        self.run = patcher.start()
        self.addCleanup(patcher.stop)

    def send(self, entry: dict) -> None:
        shortcuts.handle_event(entry, "Cmdr", "Sys", None, {})

    def test_chat_commands_are_off_until_switched_on(self) -> None:
        self.send(_chat("!wf center"))
        self.run.assert_not_called()

    def test_a_command_runs_its_action_once_switched_on(self) -> None:
        _saved["wfmt_shortcut_chat_enabled"] = True
        for word, action_id in (("center", "center"), ("border", "border"), ("rig", "rig"), ("zoom", "zoom"), ("live", "live"), ("overlays", "overlays")):
            self.run.reset_mock()
            self.send(_chat(f"!wf {word}"))
            self.run.assert_called_once_with(action_id)

    def test_other_events_and_other_messages_do_nothing(self) -> None:
        _saved["wfmt_shortcut_chat_enabled"] = True
        self.send({"timestamp": _stamp(1), "event": "FSDJump", "Message": "!wf center"})
        self.send(_chat("hello"))
        self.send(_chat("!wf center please"))
        self.send(_chat("!wf nonsense"))
        self.run.assert_not_called()

    def test_an_old_command_is_ignored(self) -> None:
        _saved["wfmt_shortcut_chat_enabled"] = True
        self.send(_chat("!wf center", seconds_ago=shortcuts.MAX_COMMAND_AGE_S + 60))
        self.send({"event": "SendText", "Message": "!wf center"})
        self.run.assert_not_called()


class RunTests(unittest.TestCase):
    def setUp(self) -> None:
        _saved.clear()
        _saved["wfmt_shortcut_sound"] = False
        self.addCleanup(lambda: (setattr(overlay, "_hidden", False), overlay._last.clear()))

    def test_overlays_flip_the_switch_and_say_so(self) -> None:
        overlay._hidden = False
        with mock.patch.object(overlay, "set_all_hidden", lambda hidden: setattr(overlay, "_hidden", hidden)):
            self.assertEqual(shortcuts.run("overlays"), "Overlays hidden.")
            self.assertEqual(shortcuts.run("overlays"), "Overlays shown.")

    def test_center_and_border_mark_through_the_live_window_module(self) -> None:
        with mock.patch.object(mining_live_window, "mark_here", return_value="Center marked. Drive to the edge of the signal and press BRD.") as mark:
            self.assertTrue(shortcuts.run("center").startswith("Center marked"))
            mark.assert_called_once_with(False)
        with mock.patch.object(mining_live_window, "mark_here", return_value="Border marked: the signal is 4.50 km in radius.") as mark:
            shortcuts.run("border")
            mark.assert_called_once_with(True)

    def test_rig_notes_a_rig_through_the_live_window_module_and_a_sound_follows_only_when_it_worked(self) -> None:
        _saved["wfmt_shortcut_sound"] = True
        with mock.patch.object(mining_live_window, "place_rig", return_value="Rig 2 noted here.") as place, mock.patch.object(platform_support, "play_notification_sound") as sound:
            self.assertEqual(shortcuts.run("rig"), "Rig 2 noted here.")
            place.assert_called_once_with()
            sound.assert_called_once()
        with mock.patch.object(mining_live_window, "place_rig", return_value="Rig already noted here (2 placed)."), \
                mock.patch.object(platform_support, "play_notification_sound") as sound:
            shortcuts.run("rig")
            sound.assert_called_once()                       # "Rig " is the prefix of every rig message, including the already-noted one
        with mock.patch.object(mining_live_window, "place_rig", return_value="WFMT cannot read your position: be on or just above the ground."), \
                mock.patch.object(platform_support, "play_notification_sound") as sound:
            shortcuts.run("rig")
            sound.assert_not_called()

    def test_a_sound_plays_only_when_it_worked_and_is_switched_on(self) -> None:
        with mock.patch.object(mining_live_window, "mark_here", return_value="Center marked. Drive on."), \
                mock.patch.object(platform_support, "play_notification_sound") as sound:
            shortcuts.run("center")
            sound.assert_not_called()                        # the sound setting is off
            _saved["wfmt_shortcut_sound"] = True
            shortcuts.run("center")
            sound.assert_called_once()
        with mock.patch.object(mining_live_window, "mark_here", return_value="WFMT cannot read your position: be on or just above the ground."), \
                mock.patch.object(platform_support, "play_notification_sound") as sound:
            shortcuts.run("center")
            sound.assert_not_called()                        # it did not work

    def test_a_failing_action_does_not_raise(self) -> None:
        with mock.patch.object(mining_live_window, "mark_here", side_effect=RuntimeError("boom")), self.assertLogs(shortcuts.logger, level="ERROR"):
            self.assertIn("did not work", shortcuts.run("center"))

    def test_an_unknown_action_says_so(self) -> None:
        self.assertIn("Unknown", shortcuts.run("nonsense"))


class SavedKeysTests(unittest.TestCase):
    def setUp(self) -> None:
        _saved.clear()

    def test_the_defaults_are_used_until_something_is_saved(self) -> None:
        self.assertEqual(shortcuts.saved_keys(), actions.default_keys())

    def test_a_saved_key_is_used_and_a_bad_one_falls_back(self) -> None:
        _saved[actions.config_key("center")] = "F9"
        _saved[actions.config_key("border")] = "Ctrl+Alt+H"
        keys = shortcuts.saved_keys()
        self.assertEqual(keys["center"], "F9")
        self.assertEqual(keys["border"], actions.action("border").default_key)

    def test_the_hotkeys_are_not_started_off_windows(self) -> None:
        with mock.patch.object(shortcuts, "hotkeys_supported", return_value=False):
            self.assertEqual(shortcuts.start_hotkeys(), {})


class LiveWindowHelperTests(unittest.TestCase):
    def setUp(self) -> None:
        _saved.clear()

    def test_the_radar_range_steps_through_every_reach_and_wraps(self) -> None:
        from plugin import mining_coverage_render as radar
        from plugin import mining_live_window as live
        seen = []
        with mock.patch.object(live, "config", _config.config):         # the module may have been imported against another test's config stand-in
            for _ in range(len(radar.RADAR_RANGES_M) + 1):
                seen.append(live.cycle_range())
        self.assertEqual(seen[-1], seen[0], "back where it started after a full turn")
        self.assertEqual(len(set(seen)), len(radar.RADAR_RANGES_M))
        self.assertTrue(all(text.startswith("Radar reaches ") for text in seen))
        self.assertIn(float(_saved[live.CONFIG_RANGE]), radar.RADAR_RANGES_M)


if __name__ == "__main__":
    unittest.main()
