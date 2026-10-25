"""Draws the real Space Mining page (plugin/mining_render.py) with EDMC stubbed: the last prospected rock, the core asteroid line, the exact limpet count and the lines for active mining
missions against the hold. Run by test_mining_page_smoke in a subprocess so the stand-ins never leak into other tests. Exits 0 if everything holds, 1 if not, 77 if Tk is unavailable."""
import quiet_tk  # noqa: F401  (keeps the test windows from taking focus)
import dataclasses
import os
import sys
import types
from dataclasses import dataclass
from unittest import mock

repo = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, repo)
import tkinter as tk


class Any(types.ModuleType):
    def __getattr__(self, n):
        if n.startswith("__"):
            raise AttributeError(n)
        return mock.MagicMock()


for n in ("monitor", "plug", "EDMCLogging", "l10n", "killswitch", "requests", "win32api", "win32con", "win32gui", "win32process", "win32clipboard", "pywintypes", "psutil",
          "ttkHyperlinkLabel", "myNotebook", "theme"):
    sys.modules[n] = Any(n)


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

try:
    root = tk.Tk()
except tk.TclError:
    print("no display available")
    sys.exit(77)
root.withdraw()

from plugin import all_missions, current_cargo, mining_alerts, mining_render as R, mining_space as S  # noqa: E402

problems = []


def check(condition, message):
    if not condition:
        problems.append(message)


@dataclass
class Mission:
    commodity: str
    commodity_key: str
    needed_commodity_count: int


def draw():
    content = tk.Frame(root)
    bar = tk.Frame(content)
    buttons = R.PanelButtons(bar, *[tk.Button(bar) for _ in range(len(dataclasses.fields(R.PanelButtons)) - 1)])
    settings = R.PanelSettings(True, True, True, False, False, False, False)
    R.render_space_mining(content, 400, buttons, settings)
    root.update()
    return [w.cget("text") for w in content.winfo_children() if isinstance(w, tk.Label)]


repo_ = S.space_mining_repository
repo_.set_current_cmdr("Bocheaux")
repo_.start_new_run()
all_missions.view.missions = {1: Mission("Painite", "painite", 80), 2: Mission("Painite", "painite", 40)}
with mock.patch.object(current_cargo, "held", lambda: {"painite": 50}):
    texts = draw()
    check("Mission needs: Painite 50 of 120 t held (2 missions)" in texts, f"before any mining the page still shows the mission needs: {texts}")

    core = {"event": "ProspectedAsteroid", "Materials": [{"Name": "water", "Proportion": 23.6}], "MotherlodeMaterial": "Bromellite",
            "Content": "$AsteroidMaterialContent_Low;", "Content_Localised": "Material Content: Low"}
    repo_.record_prospected(core["Content"], core["Content_Localised"], core["Materials"], mining_alerts.rock_finding(core))
    repo_.update_cargo(40)
    repo_.update_limpets(6)
    texts = draw()
    check("Last rock: Water 24% (Low), core: Bromellite" in texts, f"the last rock: {texts}")
    check("Core asteroids found: 1 (last: Bromellite)" in texts, f"the core count: {texts}")
    check(any(t.startswith("Limpets launched") and "(6 on board)" in t for t in texts), f"the exact limpet count: {texts}")
    check("Mission needs: Painite 50 of 120 t held (2 missions)" in texts, f"the mission needs: {texts}")

    all_missions.view.missions = None
    check(not any(t.startswith("Mission needs") for t in draw()), "no missions: no line")

if problems:
    print("PROBLEMS:")
    for p in problems:
        print("  -", p)
    sys.exit(1)
print("MINING PAGE OK")
