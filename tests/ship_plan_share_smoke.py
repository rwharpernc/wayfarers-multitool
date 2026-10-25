"""Builds the Ship planner tab (plugin/ship_plan_tab.py) with EDMC stubbed and checks the link buttons: a pasted Coriolis or EDSY link is read, the Coriolis and EDSY link
buttons copy a link that decodes back to the build, the Open buttons hand the same link to the browser, a build too long for Coriolis is refused with a reason, and nothing happens
before a loadout is read. Run by test_ship_plan_share_smoke.py in a subprocess so the stand-ins never leak into other tests. Exits 0 if everything holds, 1 if not, 77 if Tk is unavailable."""
import quiet_tk  # noqa: F401  (keeps the test windows from taking focus)
import json
import os
import sys
from unittest import mock

repo = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, repo)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import window_fit_check as W

W.install_edmc_stubs()
import tkinter as tk

try:
    root = tk.Tk()
except tk.TclError:
    print("Tk is unavailable here")
    sys.exit(77)
root.withdraw()

from plugin import ship_links, ship_plan, ship_plan_tab

failures = []


def check(ok, message):
    if not ok:
        failures.append(message)
        print("FAIL:", message)


class Wish:
    def add_many(self, entries):
        return len(entries)


statuses = []
frame = tk.Frame(root)
frame.pack()
tab = ship_plan_tab.ShipPlanTab(frame, Wish(), statuses.append, current_ship=lambda: None)

LOADOUT = {"event": "Loadout", "Ship": "federation_corvette", "ShipName": "Big Red",
           "Modules": [{"Slot": "FrameShiftDrive", "Item": "int_hyperdrive_size5_class5", "On": True,
                        "Engineering": {"BlueprintName": "FSD_LongRange", "Level": 5, "ExperimentalEffect": "special_fsd_heavy", "Quality": 1.0}},
                       {"Slot": "CargoHatch", "Item": "modularcargobaydoor", "On": True}]}

tab.share("coriolis", "copy")
check(statuses and "Read a loadout first" in statuses[-1], f"nothing happens before a loadout is read: {statuses}")

check(tab.load_text(ship_links.edsy_url(LOADOUT)), f"a pasted EDSY link is read: {statuses}")
check(tab.selected_build() is not None and tab.selected_build().ship_id == "federation_corvette", "the build is selected")

for site, maker in (("coriolis", ship_links.coriolis_url), ("edsy", ship_links.edsy_url)):
    tab.share(site, "copy")
    copied = root.clipboard_get()
    check(copied.startswith(("https://coriolis.io/import?data=", "https://edsy.org/#/I=")), f"{site}: a link was copied: {copied[:60]}")
    back = ship_links.decode_link(copied)
    check(back.get("Ship") == "federation_corvette" and len(back.get("Modules", [])) == 2, f"{site}: the copied link decodes to the build")
    check("Copied" in statuses[-1], f"{site}: the status says it copied: {statuses[-1]}")
    with mock.patch.object(ship_plan_tab.webbrowser, "open") as opened:
        tab.share(site, "open")
    check(opened.call_count == 1 and ship_links.decode_link(opened.call_args[0][0]).get("Ship") == "federation_corvette", f"{site}: Open hands the link to the browser")
    check("Opened" in statuses[-1], f"{site}: the status says it opened: {statuses[-1]}")

# a build whose Coriolis link is too long is refused for Coriolis only
import hashlib


def noise(*parts):
    return hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()


big = dict(LOADOUT)
big["Modules"] = [{"Slot": f"Slot{i}", "Item": f"int_item_{noise(i)[:24]}", "On": True,
                   "Engineering": {"BlueprintName": f"Blueprint_{noise(i, 'b')[:16]}", "Level": 5,
                                   "Modifications": [{"Label": f"Mod{noise(i, j)[:12]}", "Value": int(noise(i, j, 'v')[:6], 16) / 7.0,
                                                      "OriginalValue": int(noise(i, j, 'o')[:6], 16) / 3.0} for j in range(8)]}}
                  for i in range(40)]
tab.load_text(json.dumps(big))
with mock.patch.object(ship_plan_tab.webbrowser, "open") as opened:
    tab.share("coriolis", "open")
check(opened.call_count == 0 and "refuses" in statuses[-1], f"Coriolis refuses a very long link: {statuses[-1]}")
tab.share("edsy", "copy")
check("Copied the EDSY link" in statuses[-1], f"the EDSY link is still offered for it: {statuses[-1]}")

# an unusable link says why and leaves the last plan alone
ok = tab.load_text("https://edsy.org/#/L=AbCdEf")
check(not ok and "EDSY's own code" in statuses[-1], f"an unusable link is explained: {statuses[-1]}")

# the modules in storage show against the build: a full match, a partial one, and none
from plugin import stored_modules


class Book:
    cmdr = "Test Pilot"

    def __init__(self, modules, asof=True):
        self._modules, self._asof = modules, asof

    def asof(self, _cmdr):
        return {"t": "2026-10-20T10:00:00Z"} if self._asof else None

    def modules(self, _cmdr):
        return self._modules

    def where(self, _cmdr, _module):
        return "Test Dock (Alpha)"


def stored(item, blueprint="", level=0):
    return {"i": item, "n": item, "e": blueprint, "l": level, "h": False, "s": "Alpha", "m": 1, "c": None, "t": None, "x": False, "p": False}


frame2 = tk.Frame(root)
frame2.pack()
held = ship_plan_tab.ShipPlanTab(frame2, Wish(), statuses.append, current_ship=lambda: None,
                                 module_book=Book([stored("int_hyperdrive_size5_class5", "FSD_LongRange", 5)]))
held.load_text(json.dumps(LOADOUT))
check(held._matches and held._matches[0].kind == stored_modules.FULL, f"a stored module with the build's engineering is a full match: {held._matches}")
check("1 in storage" in held._summary.cget("text"), f"the summary counts the match: {held._summary.cget('text')}")
held._pick("0")
check("In storage" in held._note.cget("text") and "Test Dock (Alpha)" in held._note.cget("text"), f"the note says where: {held._note.cget('text')}")

other = ship_plan_tab.ShipPlanTab(tk.Frame(root), Wish(), statuses.append, current_ship=lambda: None,
                                  module_book=Book([stored("int_hyperdrive_size5_class5", "FSD_FastBoot", 2)]))
other.load_text(json.dumps(LOADOUT))
check(other._matches[0].kind == stored_modules.PARTIAL and "different engineering" in other._matches[0].detail, f"other engineering is a partial match: {other._matches}")

empty = ship_plan_tab.ShipPlanTab(tk.Frame(root), Wish(), statuses.append, current_ship=lambda: None, module_book=Book([], asof=False))
empty.load_text(json.dumps(LOADOUT))
check(all(m.kind == "" for m in empty._matches), "no stored list, no match")

root.destroy()
if failures:
    print(f"{len(failures)} failure(s)")
    sys.exit(1)
print("SHIP SHARE OK")
