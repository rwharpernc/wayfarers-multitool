"""Checks the shared type-ahead for body and ring names, ships and comma-separated commodity lists (plugin/name_suggestions.py) with EDMC stubbed: the matching order and cap, the bodies
WFMT holds for a system, a box that follows the system box beside it, taking one commodity from a list, and the body and ship kinds of form field. Run by
test_name_suggestions.py in a subprocess so the stand-ins never leak into other tests. Exits 0 if everything holds, 1 if not, 77 if Tk is unavailable."""
import os
import sys
import types
from unittest import mock

os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, ".")
import tkinter as tk


class Any(types.ModuleType):
    def __getattr__(self, n):
        if n.startswith("__"):
            raise AttributeError(n)
        return mock.MagicMock()


for n in ("monitor", "plug", "EDMCLogging", "l10n", "killswitch", "requests", "win32api", "win32con", "win32gui", "win32process", "win32clipboard", "pywintypes", "psutil", "ttkHyperlinkLabel"):
    sys.modules[n] = Any(n)
nb = Any("myNotebook")
nb.Frame, nb.Label, nb.Button, nb.Checkbutton = tk.Frame, tk.Label, tk.Button, tk.Checkbutton
sys.modules["myNotebook"] = nb
theme = Any("theme")
theme.theme = mock.MagicMock()
theme.theme.active = None
theme.theme.THEME_DEFAULT = 0
sys.modules["theme"] = theme
saved = {}


class Cfg:
    def get_str(self, key, default=""):
        return saved.get(key, default) or ""

    def get_bool(self, key, default=False):
        return saved.get(key, default)

    def get_int(self, key, default=0):
        return saved.get(key, default)

    def get(self, key, default=None):
        return saved.get(key, default)

    def set(self, key, value):
        saved[key] = value


cfgmod = types.ModuleType("config")
cfgmod.appname = "EDMarketConnector"
cfgmod.config = Cfg()
cfgmod.user_agent = "t"
cfgmod.appversion = lambda: "5.13.0"
sys.modules["config"] = cfgmod

try:
    root = tk.Tk()
except tk.TclError:
    print("no display available")
    sys.exit(77)
root.geometry("600x300")
root.update()
from plugin import mining_hotspots, name_suggestions as N, system_survey, trade_ship
from plugin.uikit.form import Field, FormDialog

problems = []


def check(condition, message):
    if not condition:
        problems.append(message)


def pump():
    root.update_idletasks()
    root.update()


# --- the matching ---------------------------------------------------------------------------------------------------------------------------
names = ["Sol 3", "Sol A Ring", "Alpha Centauri A 1", "Sol B Ring", "sol 3", "Earth"]
check(N.match(names, "sol") == ["Sol 3", "Sol A Ring", "Sol B Ring"], f"names that start with the text, once each, A to Z: {N.match(names, 'sol')}")
check(N.match(names, "ring") == ["Sol A Ring", "Sol B Ring"], "then names that contain it")
check(N.match(names, "A R")[:1] == ["Sol A Ring"], "a space matches inside the name")
check(N.match(names, "")[:2] == ["Alpha Centauri A 1", "Earth"], "an empty box offers the first names")
check(N.match(names, "zzz") == [], "no match offers nothing")
check(len(N.match([f"B{n}" for n in range(100)], "B")) == N.MAX_SUGGESTIONS, "the list is capped")

# --- ships ------------------------------------------------------------------------------------------------------------------------------------
ships = trade_ship.known_ships()
check("Imperial Clipper" in ships and "Fer-de-Lance" in ships and ships == sorted(ships, key=str.casefold), f"the ship names, A to Z: {ships[:4]}")
check(N.match(ships, "imp")[0].startswith("Imperial"), "typing imp suggests the Imperial ships")

# --- bodies from what WFMT holds ---------------------------------------------------------------------------------------------------------------
survey = system_survey.survey
survey.reset("Sol")
survey.bodies = {1: system_survey.Body(1, "Sol 3", "3"), 2: system_survey.Body(2, "Sol A Belt Cluster 1", "A Belt Cluster 1")}
mining_hotspots.hotspot_repository.add(mining_hotspots.Hotspot(system="Sol", body="Sol 4", material="Painite")) if hasattr(mining_hotspots.hotspot_repository, "add") else None
found = N.body_names("Sol")
check("Sol 3" in found and "Sol A Belt Cluster 1" in found, f"the scanned bodies of the system: {found}")
check(N.body_names("Sol") == N.body_names(""), "with no system given, the system the survey is on")
check(N.body_names("Barnard's Star") == [] or "Sol 3" not in N.body_names("Barnard's Star"), "another system does not get this system's bodies")

# --- the boxes ---------------------------------------------------------------------------------------------------------------------------------
frame = tk.Frame(root)
frame.pack()
system_var, body_var = tk.StringVar(value="Sol"), tk.StringVar()
body_entry = tk.Entry(frame, textvariable=body_var)
body_entry.pack()
body_box = N.attach_bodies(body_entry, body_var, lambda: system_var.get())
body_var.set("sol 3")
check(body_box.matches() == [] or "Sol 3" not in body_box.matches(), "a name already typed in full is not offered again")
body_var.set("Sol A")
check("Sol A Belt Cluster 1" in body_box.matches(), f"the body box suggests the system's bodies: {body_box.matches()}")
system_var.set("Elsewhere")
check("Sol A Belt Cluster 1" not in body_box.matches(), "and follows the system box")

ship_var = tk.StringVar(value="Fer")
ship_entry = tk.Entry(frame, textvariable=ship_var)
ship_entry.pack()
ship_box = N.attach_ships(ship_entry, ship_var)
check("Fer-de-Lance" in ship_box.matches(), f"the ship box suggests ships: {ship_box.matches()}")

list_var = tk.StringVar(value="Painite, Plat")
list_entry = tk.Entry(frame, textvariable=list_var)
list_entry.pack()
list_box = N.attach_commodity_list(list_entry, list_var)
check("Platinum" in list_box.matches(), f"a comma list suggests the commodity being typed: {list_box.matches()}")
list_box._set_text("Platinum")
check(list_var.get() == "Painite, Platinum", f"and taking one replaces only that one: {list_var.get()!r}")

# --- the forms ----------------------------------------------------------------------------------------------------------------------------------
sys_var = tk.StringVar(value="Sol")
for kind in ("body", "ship", "system", "commodity"):
    widget = FormDialog._input(frame, Field("x", "X", kind, "", values=["Gold"]), tk.StringVar(), {"system": sys_var})
    check(any(str(tag).startswith("WfmtSystemSuggest") for tag in widget.bindtags()), f"a {kind} field in a form has the type-ahead")
# a Body field built before the System field still follows it (the system is looked up when the box is used)
from plugin import name_suggestions as _names  # noqa: E402
seen = {}
real_bodies = _names.attach_bodies
_names.attach_bodies = lambda entry, var, system, on_pick=None: seen.update(system=system) or real_bodies(entry, var, system, on_pick)
try:
    later = {}
    FormDialog._input(frame, Field("body", "Body", "body", ""), tk.StringVar(), later)
    later["system"] = tk.StringVar(value="Sol")
finally:
    _names.attach_bodies = real_bodies
check(seen["system"]() == "Sol", f"a Body field placed before the System field follows it: {seen['system']()!r}")
plain = FormDialog._input(frame, Field("x", "X", "text", ""), tk.StringVar(), {"system": sys_var})
check(not any(str(tag).startswith("WfmtSystemSuggest") for tag in plain.bindtags()), "a plain text field has none")

if problems:
    print("PROBLEMS:")
    for line in problems:
        print("  -", line)
    sys.exit(1)
print("NAME SUGGESTIONS OK")
