"""Builds the money and materials pop-out windows (Trade History, Credits Ledger, Materials, Material trader, Engineering with its Blueprints, Wishlist, Ship planner,
Upgrade planner and Engineers tabs) with EDMC stubbed and long data (60-character station names, 40-character system names, 24-character commander names, credits in
the billions), and runs the layout checker (window_fit_check.py) at the window's minimum size, 640 px wide and 1600 px wide. Fails on text cut off, controls pushed outside
the window, labels that cannot wrap and tables whose columns do not fit or do not use a wide window. Run by test_window_fit_money_smoke.py in a subprocess so the stand-ins
never leak into other tests. Exits 0 if everything holds, 1 if not, 77 if Tk is unavailable."""
import quiet_tk  # noqa: F401  (keeps the test windows from taking focus)
import json
import os
import sys
import tempfile
import time
from unittest import mock

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

from plugin import (blueprints, blueprints_window, ledger_window, lifetime_stats, material_trader_window, material_traders, materials_panel,  # noqa: E402
                    materials_window, trade_history as H, trade_history_window, trade_ledger as L)

problems, notes = [], []
A = (F.SYSTEM, F.STATION)
B = (F.SYSTEM[::-1], F.STATION[::-1])
FUEL = "Hydrogen Fuel Rods of the Long Name Kind"


def buy(name, count, price, stamp):
    return {"event": "MarketBuy", "Type": name.lower(), "Type_Localised": name, "Count": count, "BuyPrice": price, "TotalCost": count * price, "timestamp": stamp}


def sell(name, count, price, paid, stamp):
    return {"event": "MarketSell", "Type": name.lower(), "Type_Localised": name, "Count": count, "SellPrice": price, "TotalSale": count * price,
            "AvgPricePaid": paid, "timestamp": stamp}


def session(cmdr, start):
    ledger = L.new_ledger(cmdr, f"Journal.{cmdr}.log", started=start, credits=F.BIG)
    L.apply_trade_event(ledger, buy(FUEL, 1265, 5655, "2026-10-09T10:12:08Z"), A)
    L.apply_trade_event(ledger, {"event": "RefuelAll", "Cost": 10, "timestamp": "2026-10-09T10:15:00Z"}, A)
    L.note_jump(ledger, {"event": "FSDJump", "JumpDist": 31.2})
    L.apply_trade_event(ledger, sell(FUEL, 1265, 6979, 5655, "2026-10-09T10:40:00Z"), B)
    L.add_route(ledger, {"t": "2026-10-09T10:05:00Z", "start": F.STATION, "total": 5, "hops": [{"from": F.SYSTEM, "to": F.SYSTEM[::-1]}]})
    L.add_search(ledger, {"t": "2026-10-09T10:20:00Z", "side": "buy", "commodity": FUEL, "tons": 10, "scope": "galaxy", "best": None})
    return H.build_record(
        ledger, cmdr, ship="Panther Clipper Mk II of the Wayward Nomads Squadron", pad="large", credits_end=F.BIG + 5_000_000,
        stock=[{"name": "Gold", "tons": 5, "cost": 500}], hold=[{"name": "Gold", "tons": 5}], capacity=1265,
        carriers=[{"type": "Fleet carrier", "name": F.STATION, "capacity": 23720, "cargo": 5060, "free": 18660, "reserved": 0}],
        saved_at="2026-10-09T11:00:00Z")


# --- Trade History ---------------------------------------------------------------------------------------------------------------------
book = H.HistoryBook()
book.save(session(F.COMMANDER, "2026-10-09T05:36:05Z"))
book.save(session("Mactavious", "2026-10-08T20:00:00Z"))
trade_history_window.show(root, book, lambda: None)
window = trade_history_window._window
F.pump(root)
F.check_views(root, window._toplevel, "Trade History", F.tab_views(window._tabs), problems, notes)
window.close()

# --- Credits Ledger --------------------------------------------------------------------------------------------------------------------
day = {"trade": F.BIG, "exploration": F.BIG, "exobiology": F.BIG, "missions": F.BIG, "vouchers": F.BIG}
record = {"at": "", "at_seen": [], "backfilled": 1, "by_day": {f"2026-10-{n:02d}": dict(day) for n in range(1, 21)}}
life = lifetime_stats.parse({
    "event": "Statistics", "timestamp": "2026-10-20T10:00:00Z",
    "Trading": {"Market_Profits": F.BIG * 100, "Resources_Traded": F.BIG, "Markets_Traded_With": 5000, "Highest_Single_Transaction": F.BIG, "Average_Profit": F.BIG},
    "Mining": {"Mining_Profits": F.BIG, "Quantity_Mined": 9999999},
    "Exobiology": {"Organic_Data_Profits": F.BIG, "Organic_Species_Encountered": 4000},
    "FLEETCARRIER": {"FLEETCARRIER_TOTAL_JUMPS": 1000, "FLEETCARRIER_DISTANCE_TRAVELLED": 123456.0, "FLEETCARRIER_EXPORT_TOTAL": 100000,
                     "FLEETCARRIER_IMPORT_TOTAL": 200000, "FLEETCARRIER_TRADEPROFIT_TOTAL": F.BIG}})
controller = mock.MagicMock()
controller.record.return_value = record
controller.cmdr = F.COMMANDER
controller.status = "Rebuilt from " + "a very long list of journal files " * 6
controller.rebuilding.return_value = False
controller.lifetime.return_value = life
ledger_window.show(root, controller)
win = ledger_window._window
F.pump(root)
F.check_views(root, win._shell.window, "Credits Ledger", F.tab_views(win._tabs), problems, notes)
win.close()

# --- Materials, Material trader --------------------------------------------------------------------------------------------------------
folder = tempfile.mkdtemp()
panel = materials_panel.MaterialsController()
mbook = materials_panel.book
mbook.load(folder)
materials_panel.wishlist.load(folder)
materials_panel.engineer_book.load(folder)
panel.handle_event({"event": "LoadGame"}, F.COMMANDER, F.SYSTEM, None, {})
mbook.apply_event({"event": "Materials", "Raw": [{"Name": "iron", "Count": 300}, {"Name": "tin", "Count": 12}, {"Name": "carbon", "Count": 120}],
                   "Manufactured": [{"Name": "gridresistors", "Count": 40}], "Encoded": [{"Name": "legacyfirmware", "Count": 7}]})
for n in range(12):
    mbook.apply_event({"event": "MaterialCollected", "Category": "Raw", "Name": f"mat{n}", "Name_Localised": "Long Material Name " * 4, "Count": 1})
materials_window.show(root, mbook, panel)
mwin = materials_window._window
F.pump(root)
F.check_views(root, mwin._shell.window, "Materials", None, problems, notes)
materials_window.close()


def fake_find(origin, kind, radius, pad):
    traders = tuple(material_traders.Trader(F.STATION, F.SYSTEM, "Planetary Outpost of the Long Name Kind", bool(n % 2), 12345.6, 123456.0, "Large")
                    for n in range(5))
    return material_traders.Result(F.SYSTEM + F.SYSTEM, kind, radius, traders)


material_trader_window.find_traders = fake_find
material_trader_window.show(root, mbook, panel)
twin = material_trader_window._window
F.pump(root)
twin._origin.set(F.SYSTEM + F.SYSTEM)
twin._find()
end = time.monotonic() + 5
while twin._busy and time.monotonic() < end:
    F.pump(root, 1)
    time.sleep(0.02)
F.pump(root)
F.check_views(root, twin._shell.window, "Material trader", None, problems, notes)
material_trader_window.close()

# --- Engineering -----------------------------------------------------------------------------------------------------------------------


def module(slot, item, blueprint, level):
    return {"Slot": slot, "Item": item, "On": True, "Engineering": {"Engineer": "Someone", "EngineerID": 300000, "BlueprintName": blueprint,
                                                                      "Level": level, "Quality": 0.5}}


loadout = {"event": "Loadout", "Ship": "federation_corvette", "ShipName": "The Pride of the Wayward Nomads Squadron Fleet Number One",
           "Modules": [module("FrameShiftDrive", "int_hyperdrive_size5_class5", "FSD_LongRange", 5),
                       module("HugeHardpoint1", "hpt_beamlaser_fixed_huge", "Weapon_LongRange", 3),
                       module("Armour", "asp_armour_grade1", "Armour_HeavyDuty", 2)]}
wish = materials_panel.wishlist
panel.handle_event({"event": "EngineerProgress", "Engineers": [
    {"Engineer": "Felicity Farseer", "EngineerID": 300100, "Progress": "Unlocked", "RankProgress": 40, "Rank": 3},
    {"Engineer": "Lei Cheung", "EngineerID": 300120, "Progress": "Invited"},
    {"Engineer": "Eleanor Bresa", "EngineerID": 400011, "Progress": "Known"}]}, F.COMMANDER, F.SYSTEM, None, {})
for blueprint in blueprints.grades_for("Frame Shift Drive", "Increased FSD Range"):
    wish.add(blueprint.id, 2)
blueprints_window.show(root, wish, materials_panel.holdings, materials_panel.engineer_book)
bwin = blueprints_window._window
F.pump(root)
bwin._query.set("increased fsd range")
bwin._fill_blueprints()
bwin._pick(blueprints.grades_for("Frame Shift Drive", "Increased FSD Range")[-1].id)
bwin._ship_plan.load_text(json.dumps(loadout))
F.pump(root)
F.check_views(root, bwin._shell.window, "Engineering", F.tab_views(bwin._tabs), problems, notes)
blueprints_window.close()

root.destroy()
for line in notes:
    print("note:", line)
if problems:
    print("PROBLEMS:\n  " + "\n  ".join(problems))
    sys.exit(1)
print("WINDOW FIT MONEY OK")
