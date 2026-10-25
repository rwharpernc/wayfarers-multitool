"""A `Location` inside a planetary ring sets the current ring on the Space Mining page like a `SupercruiseExit` does (plugin/mining_panel.py), so a relog or an EDMC restart in a ring
does not leave the ring unknown. The panel's journal handling is driven directly, with no window. Run by test_mining_panel_location in a subprocess so the EDMC stand-ins never leak
into other tests. Exits 0 if everything holds, 1 if not, 77 if Tk is unavailable."""
import os
import sys
import types
from unittest import mock

repo = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, repo)
try:
    import tkinter  # noqa: F401
except ImportError:
    sys.exit(77)


class Any(types.ModuleType):
    def __getattr__(self, n):
        if n.startswith("__"):
            raise AttributeError(n)
        return mock.MagicMock()


for n in ("monitor", "plug", "EDMCLogging", "l10n", "killswitch", "requests", "win32api", "win32con", "win32gui",
          "win32process", "win32clipboard", "pywintypes", "psutil", "ttkHyperlinkLabel", "myNotebook"):
    sys.modules[n] = Any(n)
theme = Any("theme")
theme.theme = mock.MagicMock()
theme.theme.active = None
theme.theme.THEME_DEFAULT = 0
sys.modules["theme"] = theme


class Cfg:
    default_journal_dir = ""

    def get_str(self, key, default=""):
        return default or ""

    def get_bool(self, key, default=False):
        return default

    def get_int(self, key, default=0):
        return default

    def get(self, key, default=None):
        return default

    def set(self, key, value):
        pass


cfgmod = types.ModuleType("config")
cfgmod.appname = "EDMarketConnector"
cfgmod.config = Cfg()
cfgmod.user_agent = "WFMT-test"
cfgmod.appversion = lambda: "5.13.0"
sys.modules["config"] = cfgmod

from plugin import mining_panel as MP  # noqa: E402

problems = []


def check(condition, message):
    if not condition:
        problems.append(message)


repo_ = MP.space_mining.space_mining_repository
repo_.set_current_cmdr("Test Cmdr")
panel = object.__new__(MP.MiningPanelController)
panel._backfilling = False
panel._srv_out = False
panel.seed_bodies = mock.Mock()
panel._check_ring_reserve = mock.Mock()
lookup = [False]
MP._cfg_bool = lambda key, default: lookup[0] if key == MP._CFG_EDSM_RESERVE_LOOKUP_ENABLED else default
MP.body_survey.system_body_survey.on_system_changed = mock.Mock()


def send(entry):
    panel.handle_event(entry, None, entry.get("StarSystem"), None, {})


RING = {"event": "Location", "StarSystem": "HIP 1", "Body": "HIP 1 2 A Ring", "BodyType": "PlanetaryRing"}
send(RING)
check(repo_.current_ring() == ("HIP 1", "HIP 1 2 A Ring"), f"a Location in a ring sets the ring: {repo_.current_ring()}")
check(not panel._check_ring_reserve.called, "no reserve lookup while the setting is off")
lookup[0] = True
send(RING)
check(panel._check_ring_reserve.call_args_list == [mock.call("HIP 1", "HIP 1 2 A Ring")], f"the reserve lookup runs when the setting is on: {panel._check_ring_reserve.call_args_list}")
send({"event": "Location", "StarSystem": "HIP 1", "Body": "HIP 1 A", "BodyType": "Star"})
check(repo_.current_ring() is None, "a Location somewhere that is not a ring clears it")
panel._backfilling = True
send(RING)
check(repo_.current_ring() == ("HIP 1", "HIP 1 2 A Ring") and len(panel._check_ring_reserve.call_args_list) == 1, "a backfill sets the ring but looks nothing up")

if problems:
    print("PROBLEMS:", len(problems))
    for line in problems:
        print(" -", line)
    sys.exit(1)
print("MINING PANEL LOCATION OK")
