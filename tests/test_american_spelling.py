"""
No British spellings in WFMT's own code, text or docs.

The project writes American English (color, tons, Colonization; see docs/DEVELOPMENT.md). This scans the code, tests, scripts and docs for the
spellings that were replaced, so one does not slip back in. Names that belong to the game or another program are not ours to
change and are listed below: the journal's `Colonisation...` events, mission and station names, and the old names that
`plugin/legacy_names.py` moves saved data away from.

Pure logic - reads files only. Run with:
    python -m unittest discover -s tests
"""

from __future__ import annotations

import os
import re
import unittest

_ROOT = os.path.join(os.path.dirname(__file__), "..")
_FOLDERS = ("plugin", "tests", "scripts", "docs", "docker", ".github", ".githooks")
_TOP_FILES = ("README.md", "CHANGELOG.md", "THIRD-PARTY-NOTICES.md", "load.py")
_SKIP_DIRS = {"__pycache__", "node_modules", "dist", ".git"}
_EXTENSIONS = (".py", ".md", ".mjs", ".js", ".txt", ".yml", ".yaml", ".sh", ".ps1", ".toml", ".cfg", ".csv")

# Files that name the old spellings on purpose, or hold the game's own names.
_EXEMPT = {
    os.path.join("plugin", "legacy_names.py"),
    os.path.join("tests", "test_legacy_names.py"),
    os.path.join("tests", "test_american_spelling.py"),
    os.path.join("plugin", "blueprints_data.py"),
    os.path.join("plugin", "trade_commodities_data.py"),
}

# The game's, Raven Colonial's and EDMCModernOverlay's own names, which keep their spelling. They are removed before the scan.
_GAME_NAMES = (
    "Mission_ColonisationDelivery", "Mission_ColonisationBeacon", "ColonisationConstructionDepot", "ColonisationContribution",
    "ColonisationSystemClaim", "ColonisationBeaconDeployed", "ColonisationShip", "colonisationConstructionDepot",
    "colonisationship", "(?:Colonisation|Colonization)", "normalise_legacy_payload",
)
# Mentions of the old data file names and settings, in the notes that explain the rename. A line marked "game spelling" matches
# the game's own text on purpose, and one that says "old name" explains the rename.
_OLD_NAME_LINES = ("`colonisation_*.json`", "`wfmt_colonisation_*`")

_BRITISH = re.compile(
    r"(?<![A-Za-z])\w*(?:tonnes?|colour|analysed|analysing|metres?|centres?|centred|neighbour|canonicalis|normalis|recognis|"
    r"summaris|serialis|optimisation|synchronis|sanitiser|localisation|colonis)\w*|(?<![A-Za-z])grey(?![A-Za-z]*(?:beard))",
    re.IGNORECASE,
)


def _files():
    for folder in _FOLDERS:
        for base, dirs, names in os.walk(os.path.join(_ROOT, folder)):
            dirs[:] = [d for d in dirs if d not in _SKIP_DIRS]
            for name in names:
                if name.endswith(_EXTENSIONS):
                    yield os.path.join(base, name)
    for name in _TOP_FILES:
        path = os.path.join(_ROOT, name)
        if os.path.isfile(path):
            yield path


class AmericanSpellingTests(unittest.TestCase):
    def test_our_own_code_and_text_use_american_spellings(self) -> None:
        found = []
        for path in sorted(_files()):
            rel = os.path.relpath(path, _ROOT)
            if rel in _EXEMPT:
                continue
            with open(path, encoding="utf-8", errors="ignore") as handle:
                for number, line in enumerate(handle, 1):
                    if any(old in line for old in _OLD_NAME_LINES) or any(mark in line for mark in ("game spelling", "old name", "old spelling")):
                        continue
                    for name in _GAME_NAMES:
                        line = re.sub(name, "", line)
                    for match in _BRITISH.finditer(line):
                        word = match.group(0)
                        if word.lower().startswith(("optimistic", "optimised")):
                            continue
                        found.append(f"{rel}:{number}: {word}")
        self.assertEqual(found, [], "British spelling: use the American one (see docs/DEVELOPMENT.md), or add a game name to _GAME_NAMES")


if __name__ == "__main__":
    unittest.main()
