"""Builds the Stored modules tab (EDMC stubbed) with no list, then with a list, and checks what it shows and that the filter narrows it. Run by
test_stored_modules.py in a subprocess so the stand-ins never leak into other tests. Exits 0 if everything holds, 1 if not, 77 if Tk is unavailable."""
import quiet_tk  # noqa: F401  (keeps the test windows from taking focus)
import os
import sys
import tempfile

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

from plugin import ship_modules_tab, stored_modules  # noqa: E402

problems = []
book = stored_modules.ModuleBook()
book.load(tempfile.mkdtemp())
book._cmdr, book._catching = "Test Pilot", False
frame = tk.Frame(root)
frame.pack()
cmdr = ["Test Pilot"]
tab = ship_modules_tab.StoredModulesTab(frame, book, lambda: cmdr[0])
if "Open Module Storage" not in tab._fresh.cget("text"):
    problems.append("no explanation before a snapshot: " + tab._fresh.cget("text"))
book.handle({"event": "StoredModules", "timestamp": "2026-10-20T10:00:00Z", "MarketID": 1, "StationName": "Test Dock", "StarSystem": "Alpha",
             "Items": [{"Name": "$int_engine_size3_class5_name;", "Name_Localised": "Thrusters", "StarSystem": "Alpha", "MarketID": 1, "TransferCost": 0,
                        "TransferTime": 0, "Hot": False},
                       {"Name": "$int_sensors_size2_class1_name;", "Name_Localised": "Sensors", "StarSystem": "Beta", "MarketID": 2, "TransferCost": 500,
                        "TransferTime": 3600, "Hot": True}]})
tab.refresh()
if len(tab._table) != 2 or "As of the last visit to Module Storage: 20 Oct 2026, Test Dock, Alpha" not in tab._fresh.cget("text"):
    problems.append(f"list not shown: {len(tab._table)} rows, {tab._fresh.cget('text')!r}")
tab._query.set("hot")
tab.refresh()
if len(tab._table) != 1:
    problems.append(f"the filter left {len(tab._table)} rows")
cmdr[0] = "Other Pilot"
tab.refresh()
if len(tab._table) != 0 or "Open Module Storage" not in tab._fresh.cget("text"):
    problems.append("another commander saw the first one's list")
root.destroy()
if problems:
    print("PROBLEMS:\n  " + "\n  ".join(problems))
    sys.exit(1)
print("STORED MODULES TAB OK")
