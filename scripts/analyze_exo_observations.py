"""Checks the species prediction against the finds WFMT has recorded (plugin/exo_observations.py, `exo_observations.json`).

    python scripts/analyze_exo_observations.py [path to exo_observations.json]

With no path it reads the copy in EDMC's plugins folder (Windows, native Linux or Flatpak, the same folders scripts/env.mjs looks in). It prints, for each genus, how often the species the game confirmed was on the
predicted list (a miss means a rule is missing or too strict), the conditions of each miss, where each species was found, the temperature, gravity and
pressure each species was seen at beside the range its rules allow, the species found together on one body, and any finds you reviewed in the Prediction
review window. The same report is behind that window's Copy report button. Records rebuilt from the journals ("backfill") are marked: their prediction
is the current rules applied afterwards. It reads a file and changes nothing.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from plugin import exo_analysis  # noqa: E402


def _default_path() -> str:
    """The first plugins folder that exists, in the order scripts/env.mjs uses (the first one when none does)."""
    home = os.path.expanduser("~")
    if sys.platform == "win32":
        local = os.environ.get("LOCALAPPDATA") or os.path.join(home, "AppData", "Local")
        folders = [os.path.join(local, "EDMarketConnector", "plugins")]
    elif sys.platform == "darwin":
        folders = [os.path.join(home, "Library", "Application Support", "EDMarketConnector", "plugins")]
    else:
        data_home = os.environ.get("XDG_DATA_HOME") or os.path.join(home, ".local", "share")
        folders = [os.path.join(data_home, "EDMarketConnector", "plugins"),
                   os.path.join(home, ".var", "app", "io.edcd.EDMarketConnector", "data", "EDMarketConnector", "plugins")]
    folder = next((f for f in folders if os.path.isdir(f)), folders[0])
    return os.path.join(folder, "Wayfarers-Multitool", "exo_observations.json")


def main(path: str) -> int:
    try:
        with open(path, encoding="utf-8") as handle:
            bodies = json.load(handle).get("bodies", {})
    except (OSError, ValueError) as exc:
        print(f"Could not read {path}: {exc}")
        return 1
    print(exo_analysis.report_text(bodies))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else _default_path()))
