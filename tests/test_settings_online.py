"""The Online page (plugin/settings_online.py) holds real settings, once each, grouped by who is asked, and is the only place that switches them. It reads the sources,
so it needs no EDMC stand-ins and behaves the same on Windows and Linux."""
from __future__ import annotations

import os
import re
import unittest

ROOT = os.path.join(os.path.dirname(__file__), "..")


def _source(name: str) -> str:
    with open(os.path.join(ROOT, "plugin", name), "r", encoding="utf-8") as handle:
        return handle.read()


def _lookups():
    block = _source("online_lookups.py")
    block = block[block.index("LOOKUPS:"):block.index("BUTTON_ONLY")]
    return re.findall(r'\("([^"]+)", "([^"]+)", "(wfmt_\w+)", (True|False), "([^"]+)"\)', block)


def _groups():
    block = _source("online_lookups.py")
    block = block[block.index("GROUPS:"):block.index("def _entry")]
    return re.findall(r'\("([^"]+)", \(([^)]*)\), "', block)


def _hooks():
    block = _source("settings_online.py")
    block = block[block.index("HOOKS: Dict"):block.index("_vars:")]
    return re.findall(r'"(wfmt_\w+)":\s*"(\w+)\.(\w+)"', block)


class OnlineLookupsPageTests(unittest.TestCase):
    def test_every_service_is_listed_under_a_heading(self) -> None:
        headed = {service for _title, services in _groups() for service in re.findall(r'"([^"]+)"', services)}
        for what, service, _key, _default, _where in _lookups():
            self.assertIn(service, headed, f"{what}: {service} has no heading on the page, so it would not be shown")

    def test_every_hook_names_a_setting_on_the_page_and_a_function_that_exists(self) -> None:
        keys = {key for _w, _s, key, _d, _p in _lookups()}
        for key, module, function in _hooks():
            self.assertIn(key, keys, f"{key} has a hook but is not on the page")
            self.assertRegex(_source(f"{module}.py"), rf"(?m)^def {function}\(", f"{module}.{function} does not exist")

    def test_no_feature_writes_one_of_the_switches_itself(self) -> None:
        """The page is the only place that switches them: a feature may read a switch, never set it. A constant is followed to the file that defines it
        (`CFG_ENABLED` is also another feature's own setting, so the name alone says nothing)."""
        keys = {key for _w, _s, key, _d, _p in _lookups()}
        sources = {name: _source(name) for name in os.listdir(os.path.join(ROOT, "plugin")) if name.endswith(".py") and name not in ("settings_online.py", "online_lookups.py")}
        defined = {name: dict(re.findall(r'^([A-Za-z_]\w*)\s*=\s*"(wfmt_\w+)"', text, re.M)) for name, text in sources.items()}
        offenders = []
        for name, text in sources.items():
            for target in re.findall(r"config\.set\(\s*([\w\.\"]+)", text):
                if target.startswith('"'):
                    value = target.strip('"')
                elif "." in target:
                    module, _, constant = target.partition(".")
                    value = defined.get(f"{module}.py", {}).get(constant, "")
                else:
                    value = defined[name].get(target, "")
                if value in keys:
                    offenders.append(f"{name} sets {value}")
        self.assertEqual(offenders, [], "these switches belong to Settings > Online; remove the second control")

    def test_a_lookup_a_feature_cannot_work_without_warns_where_it_is_used(self) -> None:
        """Each of these shows `online_lookups.needs(...)` (or `needs_any`) at the place the feature is used; the shared text is the one wording. A file that loses
        its call fails here, so a switch cannot go off with no explanation at the place it matters."""
        where_used = (
            "trade_panel.py", "trade_watch_panel.py", "mission_sources_window.py",             # Trade lookups
            "landing_finder_window.py", "landing_finder_panel.py",                              # Nearest place to land
            "bgs_panel.py",                                                                     # BGS tick detection
            "mining_hotspot_finder_dialog.py", "mining_price_finder_dialog.py", "mining_what_pays_dialog.py", "mining_market_research_dialog.py",
            "mining_reserve_lookup_dialog.py", "mining_ledger.py", "mining_render.py",          # Mining lookups (the panel's bar, the dialogs, the Book)
            "colonization_settings.py", "colonization_window.py", "colonization_projects_window.py",      # writing to Raven Colonial
            "system_autocomplete.py",                                                           # system names (the hint under the box)
        )
        for name in where_used:
            self.assertRegex(_source(name), r"online_lookups\.needs(_any)?\(", f"{name} no longer shows the warning for the lookup it needs")

    def test_the_mining_panel_places_every_button_bar_through_the_one_that_warns(self) -> None:
        text = _source("mining_render.py")
        self.assertEqual(text.count("place_button_bar(buttons, row, _shown_buttons"), 1, "only place_bar itself may place the bar: a page that does not warns of nothing")
        self.assertGreaterEqual(text.count("place_bar(buttons, row, settings"), 6)

    def test_the_page_has_its_two_buttons_and_the_hooks_are_called_on_a_change(self) -> None:
        text = _source("settings_online.py")
        self.assertIn("def turn_all_on", text)
        self.assertIn("def turn_all_off", text)
        self.assertIn("def reset_defaults", text)
        self.assertIn("_call_hook(key)", text)
        self.assertIn("settings_online.save_settings()", _source("ui.py"))


    def test_every_entry_names_a_setting_the_code_has(self) -> None:
        everything = "".join(_source(name) for name in os.listdir(os.path.join(ROOT, "plugin")) if name.endswith(".py") and name not in ("settings_online.py", "online_lookups.py"))
        entries = _lookups()
        self.assertGreaterEqual(len(entries), 15, "the parse found too little; the test is broken")
        for what, _service, key, _default, _where in entries:
            self.assertIn(f'"{key}"', everything, f"{what}: no setting called {key}")

    def test_no_setting_is_listed_twice(self) -> None:
        keys = [key for _w, _s, key, _d, _p in _lookups()]
        self.assertEqual(len(keys), len(set(keys)))

    def test_every_place_is_a_settings_tab(self) -> None:
        """The 'where to change it' text names a top-level tab or 'Group > Tab' that the Settings build really makes (see tests/prefs_smoke.py's leaf list)."""
        real = {
            "BGS", "Colonization", "Mining", "Missions", "Powerplay", "Trade",
            "Exploration > Exploration Value", "Exploration > Boxel Survey", "Exploration > Nearest place to land",
            "Overlays > System targets", "Overlays > Route", "Overlays > Powerplay", "Every system box", "General > Updates",
        }
        for what, _service, _key, _default, where in _lookups():
            self.assertIn(where, real, f"{what}: {where} is not a Settings page")


if __name__ == "__main__":
    unittest.main()
