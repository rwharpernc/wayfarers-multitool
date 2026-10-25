"""Builds the notes, expedition, exploration and surface pop-out windows (Notes, Expedition, Expedition Log, Exploration Dashboard, Nearest place to land, Marks) with EDMC
stubbed and long data (60-character station names, 40-character system names, 120-character notes, 24-character commander names), and runs the layout checker
(window_fit_check.py) at the window's minimum size, 640 px wide and 1600 px wide. Fails on text cut off, controls pushed outside the window, labels that cannot wrap and
tables whose columns do not fit or do not use a wide window. Run by test_window_fit_places_smoke.py in a subprocess so the stand-ins never leak into other tests. Exits 0 if
everything holds, 1 if not, 77 if Tk is unavailable."""
import quiet_tk  # noqa: F401  (keeps the test windows from taking focus)
import os
import sys
import tempfile
import time

repo = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, repo)
import tkinter as tk
import window_fit_check as F

saved = F.install_edmc_stubs()
try:
    root = tk.Tk()
except tk.TclError:
    print("no display available")
    sys.exit(77)
root.withdraw()

from plugin import (expedition_log_panel as LP, expedition_log_window as LW, expedition_panel, expedition_window, explore_dashboard as DASH,  # noqa: E402
                    explore_dashboard_window as DW, landing_finder as LF, landing_finder_panel, landing_finder_window, notes_data, notes_panel, notes_window,
                    surface_marks, surface_marks_window, system_survey)

problems, notes = [], []
folder = tempfile.mkdtemp()
BODY = F.SYSTEM + " A 1 a"


def settle(done=lambda: False, seconds=5):
    end = time.monotonic() + seconds
    while time.monotonic() < end and not done():
        F.pump(root, 1)
        time.sleep(0.02)
    F.pump(root)


# --- Notes -----------------------------------------------------------------------------------------------------------------------------
controller = notes_panel.NotesController()
book = notes_panel.book
book.load(folder)
controller.handle_event({"event": "LoadGame"}, F.COMMANDER, F.SYSTEM, None, {})
for number in range(14):
    book.add(F.SYSTEM + f" {number}", BODY, F.NOTE)
notes_window.show(root, book, lambda: (F.SYSTEM, BODY))
win = notes_window._window
F.pump(root)
win._table.select(win._table._order[0], notify=True)
win._system.set(F.SYSTEM + F.SYSTEM)
win._body.set(BODY + BODY)
win._text.insert("1.0", F.NOTE * 3)
F.pump(root)
F.check_views(root, win._shell.window, "Notes", None, problems, notes)
notes_window.close()

# --- Expedition ------------------------------------------------------------------------------------------------------------------------
panel = expedition_panel.ExpeditionController()
ebook = expedition_panel.book
ebook.load(folder)
panel.handle_event({"event": "LoadGame"}, F.COMMANDER, F.SYSTEM, None, {})
trip = ebook.create("Expedition to the Far Reaches of the Galaxy " + F.COMMANDER)
for number in range(14):
    ebook.add_stop(trip.id, F.SYSTEM + f" {number}", BODY, F.NOTE, xyz=(1000.0 * number, 20.0, 25899.97))
ebook.start(trip.id)
expedition_window.show(root, ebook, panel)
win = expedition_window._window
F.pump(root)
win._table.select(win._table._order[0], notify=True)
F.pump(root)
F.check_views(root, win._shell.window, "Expedition", None, problems, notes)
expedition_window.close()

# --- Expedition Log --------------------------------------------------------------------------------------------------------------------
LP.start(folder)


def ev(entry, system=None):
    LP.handle_event(entry, F.COMMANDER, system, None, {})


ev({"event": "LoadGame", "Commander": F.COMMANDER})
ev({"event": "Loadout", "Ship": "explorer_nx", "Ship_Localised": "Caspian Explorer", "ShipName": "The Far Horizon of the Wayward Nomads", "ShipIdent": "WF-01"})
ev({"event": "Location", "StarSystem": F.SYSTEM, "SystemAddress": 1}, system=F.SYSTEM)
for number in range(3):
    run = LP.controller.start_expedition("Expedition to the Far Reaches of the Galaxy " + F.COMMANDER)
    for jump in range(5):
        ev({"event": "FSDJump", "StarSystem": F.SYSTEM + f" {jump}", "SystemAddress": jump + 2, "JumpDist": 12345.5}, system=F.SYSTEM)
    ev({"event": "MultiSellExplorationData", "TotalEarnings": F.BIG})
    ev({"event": "SellOrganicData", "BioData": [{"Value": F.BIG, "Bonus": F.BIG}]})
    LP.controller.stop_expedition()
LW.journal_folder = lambda: folder
LW.show(root, LP.book, LP.controller)
win = LW._window
F.pump(root)
win._table.select(win._table._order[0], notify=True)
F.pump(root)
F.check_views(root, win._shell.window, "Expedition Log", None, problems, notes)
LW.close()

# --- Exploration Dashboard -------------------------------------------------------------------------------------------------------------
survey = system_survey.survey
survey.reset(F.SYSTEM, 7)
survey.playing, survey.in_transit, survey.docked = True, False, False
survey.handle_event({"event": "FSSDiscoveryScan", "BodyCount": 4, "Progress": 0.5})
survey.handle_event({"event": "Scan", "BodyID": 0, "BodyName": F.SYSTEM, "StarSystem": F.SYSTEM, "StarType": "K", "StellarMass": 0.8, "DistanceFromArrivalLS": 0.0})
survey.handle_event({"event": "Scan", "BodyID": 1, "BodyName": BODY, "StarSystem": F.SYSTEM, "PlanetClass": "Water world", "MassEM": 1.1, "WasDiscovered": False,
                     "WasMapped": False, "DistanceFromArrivalLS": 123456.0, "SurfaceGravity": 11.0, "SurfaceTemperature": 300.0,
                     "Atmosphere": "a thick Oxygen atmosphere", "AtmosphereComposition": [{"Name": "Oxygen", "Percent": 99.0}]})
survey.handle_event({"event": "Scan", "BodyID": 2, "BodyName": BODY + " b", "StarSystem": F.SYSTEM, "PlanetClass": "Rocky body", "MassEM": 0.04, "Landable": True,
                     "WasFootfalled": False, "DistanceFromArrivalLS": 800.0, "SurfaceGravity": 2.0, "Materials": [{"Name": "iron", "Percent": 20.0}]})
survey.handle_event({"event": "FSSBodySignals", "BodyID": 2, "BodyName": BODY + " b", "Signals": [{"Type": "$SAA_SignalType_Biological;", "Count": 2}]})
frame = tk.Frame(root)
frame.pack()
DASH.start(folder)
DASH.build_panel(frame)
DASH.handle_event({"event": "Scan"}, F.COMMANDER, F.SYSTEM, None, {})
DASH.dashboard_status({"Flags": 0x1000000, "BodyName": BODY})
DASH.controller._open()
F.pump(root, 8)
dwin = DW._window
dwin._select_body("2")
F.pump(root)
dviews = []
for name, select in F.tab_views(dwin._tabs):
    dviews.append((name, lambda select=select: (select(), F.pump(root, 6))))
F.check_views(root, dwin._shell.window, "Exploration Dashboard", dviews, problems, notes)
DW.close()

# --- Nearest place to land -------------------------------------------------------------------------------------------------------------
lcontroller = landing_finder_panel.FinderController()
lcontroller.build_panel(frame)
lcontroller.handle_event({"event": "Loadout", "Ship": "python"}, F.COMMANDER, F.SYSTEM, None, {})
lcontroller.handle_event({"event": "FSDJump", "StarSystem": F.SYSTEM, "StarPos": [1.5, 2.5, 3.5]}, F.COMMANDER, F.SYSTEM, None, {})


def fake_find(position, pad, services, carriers, days):
    stations = tuple(LF.Place(F.STATION, F.SYSTEM, "Planetary Outpost of the Long Name Kind", False, False, 123456.0, 12345.0, 13, 14, 7,
                              ("Refuel", "Repair", "Restock", "Outfitting", "Shipyard", "Market"), "2026-10-16T00:00:00Z") for _ in range(6))
    carriers_ = tuple(LF.Place("T5M-BVZ " + F.STATION[:30], F.SYSTEM, LF.CARRIER_TYPE, True, False, 913.0, 0.0, 4, 4, 8, ("Refuel", "Repair"), "2026-10-15T00:00:00Z", "All")
                      for _ in range(3)) if carriers else ()
    return LF.Result(position, pad, tuple(services), days, stations, carriers_, carriers)


landing_finder_window.find_places = fake_find
landing_finder_window.show(root, lcontroller)
lwin = landing_finder_window._window
F.pump(root)
lwin._find()
settle(lambda: not lwin._busy)
F.check_views(root, lwin._shell.window, "Nearest place to land", None, problems, notes)
landing_finder_window.close()

# --- Marks -----------------------------------------------------------------------------------------------------------------------------
mbook = surface_marks.MarkBook()
mbook.load(folder)
mbook.set_commander(F.COMMANDER)
for number in range(14):
    mbook.add(F.STATION[:40] + f" {number}", BODY + BODY, 12.3456, -45.6789)
surface_marks_window.show(root, mbook, lambda: surface_marks.Here(BODY, 12.0, 34.0, 6000.0))
win = surface_marks_window._window
F.pump(root)
win._table.select(win._table._order[0], notify=True)
F.pump(root)
F.check_views(root, win._shell.window, "Marks", None, problems, notes)
surface_marks_window.close()

root.destroy()
for line in notes:
    print("note:", line)
if problems:
    print("PROBLEMS:\n  " + "\n  ".join(problems))
    sys.exit(1)
print("WINDOW FIT PLACES OK")
