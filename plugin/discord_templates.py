"""
How the Discord posts look: the options each report offers, the built-in presets, and the templates a commander saves and chooses.

Pure apart from the file. A template is data, not code: a name, the report it is for (the BGS report or Powerplay progress) and a set of options (which sections to show,
and a layout style). The renderers (`bgs_discord.py`, `powerplay_discord.py`) take the options and write the messages, so escaping a name and splitting a long report
under Discord's 2,000-character limit stay automatic whatever the options are, and no option can make a post ping someone. The Standard preset is the layout the posts had
before templates existed, and the renderers produce exactly that for it. Copy for Discord and Post to Discord use the same chosen template.

Presets (Standard, Compact, Detailed, Plain) cannot be changed or deleted. A commander's own templates are saved by name in `discord_templates.json` in the plugin folder
(kept across updates, and included in Back up my data, since a look is not a secret). Which template each report uses is kept in the same file for the whole installation.
The dialog that edits all this is `discord_customize.py`.
"""
from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional, Tuple

try:
    from config import appname
except ImportError:   # unit tests outside EDMC
    appname = "EDMarketConnector"

plugin_name = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
logger = logging.getLogger(f"{appname}.{plugin_name}")

STATE_FILENAME = "discord_templates.json"
BGS = "bgs"
POWERPLAY = "powerplay"
REPORTS = (BGS, POWERPLAY)
REPORT_LABELS = {BGS: "BGS Report", POWERPLAY: "Powerplay progress"}
NAME_MAX = 40
MAX_SAVED = 30                   # saved templates for each report

STANDARD = "Standard"
COMPACT = "Compact"
DETAILED = "Detailed"
PLAIN = "Plain"
PRESET_NAMES = (STANDARD, COMPACT, DETAILED, PLAIN)

SCOPE_ALL = "all"
SCOPE_WORKED = "worked"
SCOPES = (SCOPE_ALL, SCOPE_WORKED)
SCOPE_LABELS = {SCOPE_ALL: "Every system in the tick", SCOPE_WORKED: "Only systems where you acted"}

# Every option of a report, with its Standard value. The booleans are the checkboxes of the dialog (see TOGGLES); `scope` is a choice of its own.
DEFAULTS: Dict[str, Dict[str, Any]] = {
    BGS: {"heading": True, "pinned_star": True, "bold_controller": True, "states": True, "influence": True, "state_lists": True, "activity": True,
          "details": False, "compact": False, "plain": False, "scope": SCOPE_ALL},
    POWERPLAY: {"heading": True, "power": True, "links": True, "cp": True, "state": True, "activities": False, "cycle": True, "plain": False},
}

# (option, label) in the order the dialog lists them.
TOGGLES: Dict[str, List[Tuple[str, str]]] = {
    BGS: [("heading", "Heading with the tick time"), ("pinned_star", "Star on pinned systems"), ("bold_controller", "Controlling faction in bold"),
          ("states", "State changes (None to Boom)"), ("influence", "Influence and its change"), ("state_lists", "Pending, recovering and active states"),
          ("activity", "What you did (the You: lines)"), ("details", "Government and allegiance"),
          ("compact", "One line for each system"), ("plain", "No formatting marks (plain text)")],
    POWERPLAY: [("heading", "Heading"), ("power", "Your Power in the heading"), ("links", "Link each system to Inara"), ("cp", "Estimated Control Points"),
                ("state", "The system's Powerplay state"), ("activities", "Merits by activity"), ("cycle", "The cycle's total line"),
                ("plain", "No formatting marks (plain text)")],
}

PRESETS: Dict[str, Dict[str, Dict[str, Any]]] = {
    BGS: {
        STANDARD: {},
        COMPACT: {"compact": True, "state_lists": False},
        DETAILED: {"details": True},
        PLAIN: {"plain": True},
    },
    POWERPLAY: {
        STANDARD: {},
        COMPACT: {"links": False, "state": False, "cycle": False},
        DETAILED: {"activities": True},
        PLAIN: {"plain": True},
    },
}


class TemplateError(Exception):
    """A problem saving, renaming or deleting a template, worded for the commander."""


@dataclass(frozen=True)
class Template:
    name: str
    report: str
    options: Mapping[str, Any]
    preset: bool = False


def resolve(report: str, options: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    """The full options for `report`: its Standard values with `options` laid over them. Unknown options are dropped, a checkbox is a true or false, and a scope that is
    not one of the choices becomes the default. Anything missing, damaged or from a newer version is therefore safe to hand to a renderer."""
    base = dict(DEFAULTS.get(report, {}))
    for key, value in (options or {}).items():
        if key not in base:
            continue
        if key == "scope":
            base[key] = value if value in SCOPES else base[key]
        else:
            base[key] = bool(value)
    return base


def clean_name(name: Any) -> str:
    return " ".join(str(name or "").split())[:NAME_MAX]


def preset(report: str, name: str) -> Optional[Template]:
    for known in PRESET_NAMES:
        if known.casefold() == str(name).strip().casefold() and known in PRESETS.get(report, {}):
            return Template(known, report, resolve(report, PRESETS[report][known]), True)
    return None


def standard(report: str) -> Template:
    return preset(report, STANDARD)    # type: ignore[return-value]


class DiscordTemplates:
    def __init__(self, plugin_dir: Optional[str] = None) -> None:
        self._path = os.path.join(plugin_dir or os.path.dirname(os.path.abspath(__file__)), STATE_FILENAME)
        self._saved: Dict[str, Dict[str, Dict[str, Any]]] = {report: {} for report in REPORTS}      # report -> {name: options}
        self._choice: Dict[str, str] = {}
        self._load()

    # --- the file -------------------------------------------------------------------------------------------------
    def _load(self) -> None:
        try:
            with open(self._path, "r", encoding="utf-8") as handle:
                raw = json.load(handle)
        except FileNotFoundError:
            return
        except (OSError, ValueError):
            logger.warning("Could not read %s; starting without saved Discord templates", self._path)
            return
        if not isinstance(raw, dict):
            return
        for item in raw.get("templates", []) if isinstance(raw.get("templates"), list) else []:
            if not isinstance(item, dict) or item.get("report") not in REPORTS:
                continue
            name = clean_name(item.get("name"))
            if name and preset(item["report"], name) is None and len(self._saved[item["report"]]) < MAX_SAVED:
                self._saved[item["report"]][name] = resolve(item["report"], item.get("options") if isinstance(item.get("options"), dict) else {})
        choice = raw.get("choice")
        if isinstance(choice, dict):
            self._choice = {report: str(choice[report]) for report in REPORTS if isinstance(choice.get(report), str)}

    def _write(self) -> None:
        data = {"version": 1, "choice": self._choice,
                "templates": [{"report": report, "name": name, "options": options} for report in REPORTS for name, options in sorted(self._saved[report].items(), key=lambda i: i[0].casefold())]}
        tmp = self._path + ".tmp"
        try:
            with open(tmp, "w", encoding="utf-8") as handle:
                json.dump(data, handle, separators=(",", ":"), sort_keys=True)
            os.replace(tmp, self._path)
        except OSError:
            logger.warning("Could not write %s", self._path, exc_info=True)

    # --- reading -------------------------------------------------------------------------------------------------
    def names(self, report: str) -> List[str]:
        """The presets first, then the saved templates by name."""
        return [name for name in PRESET_NAMES if name in PRESETS.get(report, {})] + sorted(self._saved.get(report, {}), key=str.casefold)

    def get(self, report: str, name: str) -> Optional[Template]:
        found = preset(report, name)
        if found is not None:
            return found
        for saved_name, options in self._saved.get(report, {}).items():
            if saved_name.casefold() == str(name).strip().casefold():
                return Template(saved_name, report, dict(options), False)
        return None

    def chosen(self, report: str) -> Template:
        """The template this report is posted with: the one the commander chose, or Standard when none is chosen or it has been deleted."""
        return self.get(report, self._choice.get(report, STANDARD)) or standard(report)

    # --- changing -------------------------------------------------------------------------------------------------
    def choose(self, report: str, name: str) -> None:
        found = self.get(report, name)
        if found is not None and self._choice.get(report) != found.name:
            self._choice[report] = found.name
            self._write()

    def save(self, report: str, name: str, options: Mapping[str, Any]) -> Template:
        """Save `options` under `name` (replacing a template of that name) and choose it. A preset's name cannot be used."""
        clean = clean_name(name)
        if report not in REPORTS:
            raise TemplateError("There is no such report.")
        if not clean:
            raise TemplateError("Give the template a name.")
        if preset(report, clean) is not None:
            raise TemplateError(f"{clean} is a built-in preset and cannot be changed. Save it under a name of your own.")
        existing = next((n for n in self._saved[report] if n.casefold() == clean.casefold()), None)
        if existing is None and len(self._saved[report]) >= MAX_SAVED:
            raise TemplateError(f"You can keep {MAX_SAVED} templates for a report. Delete one first.")
        if existing is not None:
            del self._saved[report][existing]
        self._saved[report][clean] = resolve(report, options)
        self._choice[report] = clean
        self._write()
        return Template(clean, report, dict(self._saved[report][clean]), False)

    def delete(self, report: str, name: str) -> None:
        found = self.get(report, name)
        if found is None:
            return
        if found.preset:
            raise TemplateError(f"{found.name} is a built-in preset and cannot be deleted.")
        del self._saved[report][found.name]
        if self._choice.get(report, "").casefold() == found.name.casefold():
            self._choice[report] = STANDARD
        self._write()

    def rename(self, report: str, old: str, new: str) -> Template:
        found = self.get(report, old)
        clean = clean_name(new)
        if found is None:
            raise TemplateError("There is no such template.")
        if found.preset:
            raise TemplateError(f"{found.name} is a built-in preset and cannot be renamed.")
        if not clean:
            raise TemplateError("Give the template a name.")
        if preset(report, clean) is not None or any(n.casefold() == clean.casefold() and n != found.name for n in self._saved[report]):
            raise TemplateError(f"There is already a template called {clean}.")
        options = self._saved[report].pop(found.name)
        self._saved[report][clean] = options
        if self._choice.get(report, "").casefold() == found.name.casefold():
            self._choice[report] = clean
        self._write()
        return Template(clean, report, dict(options), False)


templates = DiscordTemplates()
