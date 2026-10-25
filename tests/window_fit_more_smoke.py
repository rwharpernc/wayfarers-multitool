"""Builds the pop-out windows not covered by the other window_fit scripts (Space Mining Book, Rare Goods Finder, Route Planner, Carrier Route, the Plan dialog, ...) with EDMC stubbed and long
data (60-character station names, 40-character system names, 120-character notes, 24-character commander names, credits in the billions), and runs the layout checker (window_fit_check.py)
at the window's minimum size, 640 px wide and 1600 px wide. Fails on text cut off, controls pushed outside the window, labels that cannot wrap and tables whose columns do not fit or do not
use a wide window. Run by test_window_fit_more_smoke.py in a subprocess so the stand-ins never leak into other tests. Exits 0 if everything holds, 1 if not, 77 if Tk is unavailable."""
import quiet_tk  # noqa: F401  (keeps the test windows from taking focus)
import io
import json
import os
import sys
import tempfile
import time
import types
from datetime import datetime, timedelta, timezone
from unittest import mock

from PIL import Image

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

from plugin import (bgs_window, blueprints_window, carrier_route as CR, carrier_route_panel, carrier_route_window, codex_completionist, codex_completionist_window,
                    colonization_builds_window, colonization_history_window, exo_observations, exo_review_window, expedition_log_window, expedition_plan_dialog, expedition_window,
                    inventory, inventory_suit, inventory_window, ledger_window, material_trader_window, materials_window, mining_coverage, mining_ground,
                    mining_history, mining_history_window, mining_hotspot_dialog, mining_hotspot_finder_dialog, mining_hotspot_import_export, mining_hotspots,
                    mining_ledger, mining_live_position, mining_live_window, mining_location, mining_market_research_dialog, mining_pages,
                    mining_price_finder_dialog, mining_render, mining_reserve_lookup_dialog, mining_ring_book, mining_rings, mining_rings_data as RD,
                    mining_spansh_client, mining_surface, mining_what_pays_dialog, notes_window, organic_scan, powerplay_control_lookup, powerplay_window,
                    rare_goods_window, route_planner as NP, route_planner_window, screenshots, ship_builds_data, ship_builds_dialog, ship_builds_window, stored_modules,
                    spansh_planners, surface_marks_window, trade_commodities, trade_history_window, trade_watch_data, trade_watch_panel, trade_watch_window)  # noqa: E402
from plugin.uikit import dialogs  # noqa: E402
from plugin.uikit.shell import WindowShell  # noqa: E402

problems, notes = [], []
folder = tempfile.mkdtemp()
host = tk.Toplevel(root)         # a window that is shown, for the dialogs that are transient for their parent (they stay hidden when it is not)
host.geometry("200x100+0+0")


def settle(done=lambda: False, seconds=5):
    end = time.monotonic() + seconds
    while time.monotonic() < end and not done():
        F.pump(root, 1)
        time.sleep(0.02)
    F.pump(root)


# --- Space Mining Book -----------------------------------------------------------------------------------------------------------------
RING = F.SYSTEM + " 1 A Ring"
rings = {RD.ring_key(RING + str(n)): {**RD.new_ring(RING + str(n), F.SYSTEM), "hotspots": {"Painite": 3, "Platinum": 2, "Low Temperature Diamonds": 4, "Void Opals": 1,
                                                                                           "Bromellite": 2, "Grandidierite": 1, "Monazite": 6, "Musgravite": 7},
                                      "class": "eRingClass_Icy", "reserve": "MajorResources", "seen": "2026-01-01"} for n in range(14)}
runs = [{"ring": RING + "0", "system": F.SYSTEM, "start": "2026-01-05T10:00:00Z", "refined": {"Painite": 123456}}]
history = mining_history.history
history.rings = lambda: rings
history.runs = lambda: runs
history.ready = True
mining_rings.notes.set_note(RD.ring_key(RING + "0"), F.NOTE)
mining_ring_book.show(root)
win = mining_ring_book._window
F.pump(root)
win._table.select(win._table._order[0], notify=True)
F.pump(root)
F.check_views(root, win._shell.window, "Space Mining Book", None, problems, notes)
mining_ring_book.close()

# --- Rare Goods Finder -----------------------------------------------------------------------------------------------------------------
powerplay_control_lookup.fetch_missing = lambda ids, callback: None
powerplay_control_lookup.cached = lambda id64: (True, None)
rare_goods_window.show(root, F.SYSTEM, (75.75, 48.75, 70.75), "Federation", "Democracy", None)
win = rare_goods_window._window
settle(lambda: bool(win._table._order))
win._table.select(win._table._order[0], notify=True)
F.pump(root)
F.check_views(root, win._shell.window, "Rare Goods", None, problems, notes)
rare_goods_window.close()

# --- Route Planner ---------------------------------------------------------------------------------------------------------------------


def legs(count, carrier=False):
    made = []
    for n in range(1, count + 1):
        name = F.SYSTEM + f" {n}"
        if carrier:
            made.append(CR.CarrierLeg(n, name, 499.5, 12345.0 * (count - n), 1000.0, 123.0, 12345 if n % 3 == 0 else 0, n % 2 == 0, n % 4 == 0, n % 5 == 0, market=1234.0))
        else:
            made.append(NP.Leg(n, name, 1, 123.4, 12345.0 * (count - n), n % 2 == 0, fuel_left=12.5, refuel=n % 3 == 0, inject=n % 5 == 0, scoopable=True))
    return made


loadout = {"event": "Loadout", "Ship": "federation_corvette", "ShipName": "The Pride of the Wayward Nomads Squadron Fleet Number One",
           "Modules": [{"Slot": "FrameShiftDrive", "Item": "int_hyperdrive_size5_class5", "On": True},
                       {"Slot": "FuelTank", "Item": "int_fueltank_size5_class3", "On": True},
                       {"Slot": "Slot01", "Item": "int_fuelscoop_size5_class5", "On": True}]}
ship = NP.ShipInfo()
ship.apply_loadout(loadout)
ctx = types.SimpleNamespace(ship=ship, route=NP.Route(F.SYSTEM, F.SYSTEM[::-1], legs(12)), auto_var=None, auto_copy=False, copied="", system=lambda: F.SYSTEM, address=lambda: 1,
                            start_expedition=lambda: "", review_expedition=lambda: "", clear_all=lambda: False, learn_ship=lambda: True, set_auto_copy=lambda on: None,
                            copy_next=lambda: "", set_route=lambda route: None, overlay_note=lambda: "")
route_planner_window.show(root, ctx)
win = route_planner_window._window
F.pump(root)
F.check_views(root, win._shell.window, "Route Planner", None, problems, notes)
route_planner_window.close()

# --- Carrier Route ---------------------------------------------------------------------------------------------------------------------
planner = carrier_route_panel.planner
planner.handle_event({"event": "CarrierStats", "CarrierType": "FleetCarrier", "Name": F.STATION[:30], "Callsign": "T5M-BVZ", "FuelLevel": 1000,
                      "SpaceUsage": {"TotalCapacity": 25000, "FreeSpace": 1000}}, F.COMMANDER)
planner.handle_event({"event": "CarrierLocation", "CarrierType": "FleetCarrier", "StarSystem": F.SYSTEM, "SystemAddress": 1}, F.COMMANDER)
planner._recovered.add("x")
planner.recover_once = lambda: None
route = CR.CarrierRoute(CR.FLEET, F.SYSTEM, F.SYSTEM[::-1], legs(12, carrier=True), needs="Have 12,345 t of tritium at the start (1,000 in the tank, 11,345 in the carrier's market).")
planner.route = route
carrier_route_window.show(root)
win = carrier_route_window._window
F.pump(root)
F.check_views(root, win._shell.window, "Carrier Route", None, problems, notes)
carrier_route_window.close()

# --- Plan a route of places worth visiting ---------------------------------------------------------------------------------------------
for kind in spansh_planners.TITLES:
    dialog = expedition_plan_dialog.open_dialog(root, kind, F.SYSTEM, 123.45, lambda query, stops, start_now: None)
    F.pump(root)
    F.check_views(root, dialog._shell.window, "Plan dialog " + kind, None, problems, notes)
    dialog.close()
    F.pump(root)

# --- Mining History --------------------------------------------------------------------------------------------------------------------


def trip(day, ring, rhino=False):
    stamp = lambda minute: f"2026-10-{day:02d}T12:{minute:02d}:00Z"
    return ([{"timestamp": stamp(0), "event": "Commander", "Name": F.COMMANDER}, {"timestamp": stamp(1), "event": "FSDJump", "StarSystem": F.SYSTEM, "SystemAddress": 1},
             {"timestamp": stamp(2), "event": "Undocked"},
             {"timestamp": stamp(5), "event": "SupercruiseExit", "StarSystem": F.SYSTEM, "Body": ring, "BodyType": "PlanetaryRing"},
             {"timestamp": stamp(6), "event": "LaunchDrone", "Type": "Prospector"}]
            + ([{"timestamp": stamp(6), "event": "ApproachBody", "Body": F.SYSTEM + " 2 a"}, {"timestamp": stamp(6), "event": "LaunchSRV", "SRVType": "mev_rhino"}] if rhino else [])
            + [{"timestamp": stamp(7), "event": "ProspectedAsteroid", "Content_Localised": "Material Content: High"}]
            + [{"timestamp": stamp(8), "event": "MiningRefined", "Type_Localised": "Low Temperature Diamonds"}] * 40
            + [{"timestamp": stamp(20), "event": "Docked", "StationName": F.STATION},
               {"timestamp": stamp(21), "event": "MarketSell", "Type": "lowtemperaturediamonds", "Type_Localised": "Low Temperature Diamonds", "Count": 40, "TotalSale": F.BIG}])


mined = []
for day in range(1, 11):
    mined += mining_history.runs_from(trip(day, F.SYSTEM + f" {day} A Ring", rhino=day % 2 == 0), f"Journal.2026-10-{day:02d}T100000.01.log")
history.runs = lambda: mined
history.refresh = lambda: None
history._cmdr = F.COMMANDER
history.reading = ""
for mode in (mining_history_window.D.SPACE, mining_history_window.D.SURFACE):
    mining_history_window.show(root, mode)
    win = mining_history_window._windows[mode]
    F.pump(root, 8)
    F.check_views(root, win._shell.window, "Mining History " + mode, F.tab_views(win._tabs), problems, notes)
    win.close()


# --- Surface Mining Book ---------------------------------------------------------------------------------------------------------------
repo_ = mining_hotspots.hotspot_repository
repo_.load(tempfile.mkdtemp())
repo_.set_commander(F.COMMANDER)
for number in range(14):
    repo_.add(mining_hotspots.Hotspot(F.SYSTEM, f"{F.SYSTEM} {number} a", "Low Temperature Diamonds" if number % 2 else "Painite", notes=F.NOTE, latitude=-12.3456, longitude=123.4567,
                                      folder="A folder with a very long name " + F.SYSTEM, rigs=4, signal_number=7, amount="High", density="High", mined_tons=123456))
history.bodies = lambda: {f"{F.SYSTEM.lower()} {n} b": {"body": f"{F.SYSTEM} {n} b", "system": F.SYSTEM, "locations": 4, "class": "Rocky body", "tons": 12345, "last": ""}
                          for n in range(6)}
mining_ledger.show(root)
win = mining_ledger._window
F.pump(root, 6)
first = next(iter(win._bodies._groups), None)
F.check_views(root, win._shell.window, "Surface Mining Book", None, problems, notes)
mining_ledger.close()

# --- Mining price, reserve and hotspot searches ----------------------------------------------------------------------------------------


def priced(n):
    return mining_spansh_client.StationPrice(station=F.STATION, system=F.SYSTEM, station_type="Planetary Outpost of the Long Name Kind", distance_ly=12345.67,
                                             distance_to_arrival_ls=1234567.0, is_planetary=bool(n % 2), price=F.BIG, quantity=F.BIG, small_pads=1, medium_pads=2, large_pads=3)


mining_price_finder_dialog.search_stations = lambda *a, **k: [priced(n) for n in range(6)]
mining_location.set_current_system(F.SYSTEM)
mining_price_finder_dialog.open_price_finder_dialog(root, suggested_commodities=["Low Temperature Diamonds"])
win = mining_price_finder_dialog._window
win._commodity.set("Low Temperature Diamonds")
win._search()
settle(lambda: len(win._table) == 6)
F.check_views(root, win._shell.window, "Price finder", None, problems, notes)
win.close()

raw = [{"name": F.SYSTEM + f" {n}", "reserveLevel": "PristineResources", "rings": [{"name": F.SYSTEM + f" {n} A Ring", "type": "Metallic"}, {"name": F.SYSTEM + f" {n} B Ring", "type": "Icy"}]}
       for n in range(1, 5)]
mining_reserve_lookup_dialog.fetch_bodies = lambda system: raw
mining_reserve_lookup_dialog.open_reserve_lookup_dialog(root)
win = mining_reserve_lookup_dialog._window
win._system.set(F.SYSTEM)
win._search()
settle(lambda: len(win._table) == 8)
F.check_views(root, win._shell.window, "Reserve lookup", None, problems, notes)
win.close()

mining_hotspot_finder_dialog.search_rings = lambda *a, **k: [mining_spansh_client.RingHotspot(system=F.SYSTEM, body=F.SYSTEM + " 2", ring_name=F.SYSTEM + f" 2 {n} Ring", distance_ly=12345.67,
                                                                                                distance_to_arrival_ls=1234567.0, reserve_level="Pristine", hotspot_count=12)
                                                               for n in range(6)]
mining_hotspot_finder_dialog.open_hotspot_finder_dialog(root)
win = mining_hotspot_finder_dialog._window
win._material.set("Low Temperature Diamonds")
win._search()
settle(lambda: len(win._table) == 6)
F.check_views(root, win._shell.window, "Hotspot finder", None, problems, notes)
win.close()

# --- What pays, Market research --------------------------------------------------------------------------------------------------------
for material in ("Painite", "Platinum", "Low Temperature Diamonds", "Void Opals"):
    repo_.add(mining_hotspots.Hotspot(F.SYSTEM, F.SYSTEM + " 1 a", material))
mining_what_pays_dialog.PAUSE_S = 0.0


def offer(*args, **kwargs):
    return [priced(1)]


with mock.patch.object(mining_what_pays_dialog, "search_stations", offer):
    mining_what_pays_dialog.open_dialog(root, F.SYSTEM, [], mining_ground.OwnRates([]))
    win = mining_what_pays_dialog._window
    settle(lambda: not win._busy)
    F.check_views(root, win._shell.window, "What pays", None, problems, notes)
    win.close()

stamp = (datetime.now(timezone.utc) - timedelta(hours=12)).strftime("%Y-%m-%dT%H:%M:%SZ")
market = [{"name": F.STATION, "type": "Planetary Outpost of the Long Name Kind", "is_planetary": n % 2 == 0, "distance_to_arrival": 1234567.0, "large_pads": 3, "market_updated_at": stamp,
           "market": [{"commodity": "Painite", "sell_price": F.BIG, "demand": F.BIG}, {"commodity": "Platinum", "sell_price": F.BIG, "demand": F.BIG}]} for n in range(5)]
mining_market_research_dialog.search_stations = lambda system, days: (market, len(market))
mining_market_research_dialog.open_dialog(root, F.SYSTEM, [], mining_ground.OwnRates([], {}))
win = mining_market_research_dialog._window
settle(lambda: len(win._table) >= 4)
F.check_views(root, win._shell.window, "Market research", None, problems, notes)
win.close()


# --- Mining live windows (Surface and Space) -------------------------------------------------------------------------------------------
RADIUS = 400_000.0
M_PER_DEG = 3.141592653589793 * RADIUS / 180.0
BODY_NAME = F.SYSTEM + " 2 a"
mining_surface.surface_mining_repository.set_current_cmdr(F.COMMANDER)
mining_surface.surface_mining_repository.set_current_location(F.SYSTEM, BODY_NAME)
mining_surface.surface_mining_repository.record_body_radius(BODY_NAME, RADIUS)
mining_coverage.coverage_repository.set_commander(F.COMMANDER)
mining_live_position.set_status({"Flags": mining_live_position.FLAGS_HAS_LAT_LONG, "Latitude": 10.0, "Longitude": 20.0, "Heading": 90, "PlanetRadius": RADIUS, "Altitude": 0})
repo_.add_or_merge(mining_hotspots.Hotspot(system=F.SYSTEM, body=BODY_NAME, material="Low Temperature Diamonds", rigs=4, notes=F.NOTE, latitude=10.0 + 800 / M_PER_DEG,
                                           longitude=20.0), RADIUS)
live_settings = mining_render.PanelSettings(True, True, True, True, True, True, True)
for page in (mining_pages.SURFACE_MINING, mining_pages.SPACE_MINING):
    win = mining_live_window.show(root, page, lambda: live_settings)
    F.pump(root, 8)
    F.check_views(root, win._shell.window, page + " Live", None, problems, notes)
    win.close()

# --- Hotspot import/export, the hotspot form and the ship build form -------------------------------------------------------------------
mining_hotspot_import_export.open_import_export_dialog(host)
win = mining_hotspot_import_export._window
F.pump(root)
F.check_views(root, win.window, "Import and export", None, problems, notes)
win.close()

forms = []


def check_form(form):
    """A form's height is its own (the window is only resizable sideways), so it is checked at that height, at its narrowest width, as opened and wide."""
    top = form.window
    min_w = top.wm_minsize()[0]
    opened_w, opened_h = top.winfo_width(), top.winfo_height()
    for name, width in (("narrow", min_w), ("opened", opened_w), ("wide", 1000)):
        top.geometry(f"{width}x{opened_h}")
        settle(seconds=0.12)
        for kind, text in F.check_window(root, top, top.winfo_width(), top.winfo_height(), wide=False):
            if kind in F.FAIL_KINDS:
                problems.append(f"{top.title()} @ {name}: {kind}: {text}")


for module, opener in ((mining_hotspot_dialog, lambda: mining_hotspot_dialog.open_hotspot_dialog(host, lambda spot: None, prefill_system=F.SYSTEM, prefill_body=BODY_NAME,
                                                                                                  prefill_latitude=-12.3456, prefill_longitude=123.4567)),
                       (ship_builds_dialog, lambda: ship_builds_dialog.open_ship_build_dialog(host, lambda build: None, prefill_ship="Federal Corvette"))):
    real = module.FormDialog

    class Spy(real):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            forms.append(self)

    module.FormDialog = Spy
    opener()
    form = forms[-1]
    for var in form._vars.values():
        if not var.get():
            var.set(F.NOTE[:40])
    form.set_error("Rigs must be 1 to 4.")
    F.pump(root)
    check_form(form)
    form.close()
    module.FormDialog = real


# --- Watch list ------------------------------------------------------------------------------------------------------------------------
wpanel = trade_watch_panel.WatchController()
wbook = trade_watch_panel.book
wbook.load(folder)
wpanel.handle_event({"event": "LoadGame"}, F.COMMANDER, F.SYSTEM, None, {})
for name in trade_commodities.SUGGESTIBLE[:12]:
    wbook.add(name)
sighting = trade_watch_data.Quote(F.BIG, F.BIG, F.STATION, F.SYSTEM, trade_watch_data.SPANSH, "2026-10-13T12:00:00Z", 12345.6)
wbook.set_lookups({name: trade_watch_data.Lookup((sighting,) * 3, (sighting,) * 3, F.SYSTEM, "2026-10-13T12:00:00Z") for name in wbook.watched()})
trade_watch_window.show(root, wbook, wpanel)
win = trade_watch_window._window
F.pump(root)
win._table.select(win._table._order[0], notify=True)
F.pump(root)
F.check_views(root, win._shell.window, "Watch list", None, problems, notes)
trade_watch_window.close()

# --- Ship Builds -----------------------------------------------------------------------------------------------------------------------
sbuilds = ship_builds_data.ShipBuildRepository()
sbuilds.load(tempfile.mkdtemp())
for number in range(12):
    sbuilds.add(F.COMMANDER, ship_builds_data.ShipBuild(id=str(number), ship="Federal Corvette of the Wayward Nomads Squadron", name=F.STATION, site="EDSY (E:D Shipyard)",
                                                        url="https://edsy.org/#/L=" + "A" * 200, role="Long haul explorer with a very long role name", notes=F.NOTE))
mbook = stored_modules.ModuleBook()
mbook.load(tempfile.mkdtemp())
mbook._cmdr, mbook._catching = F.COMMANDER, False
mbook.handle({"event": "StoredModules", "timestamp": "2026-10-20T10:00:00Z", "MarketID": 1, "StationName": F.STATION, "StarSystem": F.SYSTEM,
              "Items": [{"Name": f"$int_hyperdrive_size{n % 7 + 1}_class{n % 5 + 1}_name;", "Name_Localised": "Frame Shift Drive of the Long Name Kind " * 2,
                         "StorageSlot": n, "StarSystem": F.SYSTEM if n % 3 else "Sol", "MarketID": 1 if n % 2 else 77 + n, "TransferCost": F.BIG, "TransferTime": 999999,
                         "Hot": bool(n % 2), "EngineerModifications": "FSD_LongRange", "Level": 5, "Quality": 1.0, "InTransit": n % 5 == 0}
                        for n in range(30)]}, F.COMMANDER)
ship_builds_window.show(root, sbuilds, F.COMMANDER, "Federal Corvette", mbook)
win = ship_builds_window._window
F.pump(root)
F.check_views(root, win._shell.window, "Ship Builds", F.tab_views(win._tabs), problems, notes)
win.close()

# --- Inventory -------------------------------------------------------------------------------------------------------------------------
tracker = inventory.InventoryTracker()
tracker.set_commander(F.COMMANDER)
sections = {"Items": [{"Name": f"item{n}", "Name_Localised": "Long Item Name " * 4, "Count": 12345} for n in range(12)],
            "Components": [{"Name": f"comp{n}", "Name_Localised": "Long Component Name " * 3, "Count": 99999} for n in range(12)],
            "Consumables": [{"Name": f"cons{n}", "Name_Localised": "Long Consumable Name " * 3, "Count": 99999} for n in range(12)],
            "Data": [{"Name": f"data{n}", "Name_Localised": "Long Data Name " * 3, "Count": 99999} for n in range(12)]}
tracker.apply_backpack_baseline(sections)
tracker.apply_ship_locker_baseline(sections)
inventory_window.show(root, tracker, inventory_suit.SuitState())
win = inventory_window._window
F.pump(root)
F.check_views(root, win._shell.window, "Inventory", F.tab_views(win._tab_bar), problems, notes)
inventory_window.close()

# --- Exobiology review -----------------------------------------------------------------------------------------------------------------
BACTERIUM = "$Codex_Ent_Bacterial_Genus_Name;"
AURASUS = "$Codex_Ent_Bacterial_01_Name;"
obook = exo_observations.ObservationBook()
obook.load(tempfile.mkdtemp())
for number in range(10):
    body = organic_scan.BodyConditions(body_name=f"{F.SYSTEM} {number} a", planet_class="Rocky body", atmosphere="CarbonDioxide", gravity_g=0.2, temperature_k=180.0 + number * 20,
                                       pressure_atm=0.05, volcanism="", star_type="K", system_name=F.SYSTEM, system_body_types=("Rocky body",))
    obook.record(body, [BACTERIUM], BACTERIUM, AURASUS, "Bacterium Aurasus", "Teal", exo_observations.predicted_keys(BACTERIUM, body), when=f"2026-10-{number + 1:02d}T10:00:00Z")
exo_review_window.show(root, obook)
win = exo_review_window._window
F.pump(root)
F.check_views(root, win._shell.window, "Exobiology review", F.tab_views(win._tabs), problems, notes)
exo_review_window.close()

# --- My Codex --------------------------------------------------------------------------------------------------------------------------
tally = codex_completionist.CodexTally()
for number in range(14):
    tally.record({"Name": f"$Codex_Ent_{number};", "Name_Localised": "Long Codex Entry Name " * 3, "Category": "$Codex_Category_Biology;", "Category_Localised": "Biological and Geological",
                  "SubCategory": "$Codex_SubCategory_Organic_Structures;", "SubCategory_Localised": "Organic structures of the long name kind", "EntryID": 1000 + number,
                  "IsNewEntry": number % 2 == 0, "timestamp": "2026-10-01T10:00:00Z"}, F.SYSTEM)
codex_completionist_window.show(root, tally, tempfile.mkdtemp(), None)
win = codex_completionist_window._window
F.pump(root)
F.check_views(root, win._shell.window, "My Codex", F.tab_views(win._tabs), problems, notes)
win.close()


# --- Themed dialogs (plugin/uikit/dialogs.py) ------------------------------------------------------------------------------------------
LONG_PATH = "C:/Users/" + F.COMMANDER.replace(" ", "") + "/AppData/Local/EDMarketConnector/plugins/WayfarersMultitool/backups/" + "x" * 80 + ".zip"
MESSAGES = {"short": "Replace the saved data?", "note": F.NOTE, "path": "Saved to " + LONG_PATH, "unbroken": "x" * 600,
            "lines": "\n".join(f"{n}. {F.NOTE}" for n in range(30)), "huge": F.NOTE * 40}


def check_modal(label, call):
    def inspect():
        tops = [w for w in host.winfo_children() if isinstance(w, tk.Toplevel)]
        if not tops:
            problems.append(f"{label}: no dialog opened")
            return
        top = tops[-1]
        F.pump(root)
        for kind, text in F.check_window(root, top, top.winfo_width(), top.winfo_height(), wide=False):
            if kind in F.FAIL_KINDS:
                problems.append(f"{label}: {kind}: {text}")
        if top.winfo_width() > dialogs.MAX_WIDTH + 200 or top.winfo_height() > root.winfo_screenheight() - 80:
            problems.append(f"{label}: the dialog is {top.winfo_width()}x{top.winfo_height()} px")
        top.destroy()

    root.after(120, inspect)
    call()


TITLE = "Restore from backup " + F.COMMANDER
for name, message in MESSAGES.items():
    check_modal(f"info {name}", lambda: dialogs.info(host, TITLE, message))
for name in ("short", "path", "huge"):
    message = MESSAGES[name]
    check_modal(f"confirm {name}", lambda: dialogs.confirm(host, TITLE, message, yes="Restore and restart " + F.COMMANDER, no="Keep what I have now"))
for name in ("note", "lines"):
    message = MESSAGES[name]
    check_modal(f"choose {name}", lambda: dialogs.choose(host, TITLE, message, ["Replace everything with the backup", "Add to what I have", "Only " + F.COMMANDER, "Cancel"]))
    check_modal(f"prompt {name}", lambda: dialogs.prompt(host, TITLE, message, initial=F.NOTE, ok="Save the " + F.COMMANDER))
check_modal("error path", lambda: dialogs.error(host, TITLE, MESSAGES["path"]))

# --- Add a ring, and the screenshot preview --------------------------------------------------------------------------------------------
mining_ring_book.show(root)
book_window = mining_ring_book._window
book_window._add_ring()
adder = [w for w in book_window._shell.window.winfo_children() if isinstance(w, tk.Toplevel)][-1]
F.pump(root)
for var_widget in adder.winfo_children():
    if isinstance(var_widget, tk.Entry):
        var_widget.insert(0, F.NOTE)
adder.winfo_children()
for kind, text in F.check_window(root, adder, adder.winfo_reqwidth(), adder.winfo_reqheight(), wide=False):
    if kind in F.FAIL_KINDS:
        problems.append(f"Add a ring: {kind}: {text}")
adder.destroy()
mining_ring_book.close()

for size in ((7680, 1080), (1080, 7680), (64, 64)):
    buffer = io.BytesIO()
    Image.new("RGB", size, (40, 90, 160)).save(buffer, format="PNG")
    screenshots.open_folder = lambda path: None
    preview = screenshots.PreviewWindow(host, buffer.getvalue(), "Cropped screenshot", folder="C:/shots")
    for name, (width, height) in (("narrow", preview.window.wm_minsize()), ("wide", (root.winfo_screenwidth(), root.winfo_screenheight() - 80))):
        preview.window.geometry(f"{width}x{height}+0+0")
        settle(seconds=0.12)                # the picture is re-fitted a moment after a resize
        for kind, text in F.check_window(root, preview.window, preview.window.winfo_width(), preview.window.winfo_height(), wide=False):
            if kind in F.FAIL_KINDS:
                problems.append(f"Screenshot preview {size[0]}x{size[1]} @ {name}: {kind}: {text}")
    if preview.window.winfo_width() > root.winfo_screenwidth() or preview.window.winfo_height() > root.winfo_screenheight():
        problems.append(f"Screenshot preview {size}: the window is {preview.window.winfo_width()}x{preview.window.winfo_height()}, past the screen")
    preview.close()

# --- Help windows ----------------------------------------------------------------------------------------------------------------------
help_texts = {"BGS Report": bgs_window.HELP, "Engineering": blueprints_window._HELP, "Carrier Route": carrier_route_window.HELP, "My Codex": codex_completionist_window._HELP,
              "Planned Builds": colonization_builds_window._HELP, "Colonization History": colonization_history_window.HELP, "Expedition Log": expedition_log_window._HELP,
              "Plot": expedition_plan_dialog._HELP, "Expedition": expedition_window._HELP, "Credits Ledger": ledger_window.HELP, "Materials": materials_window._HELP,
              "Material trader": material_trader_window._HELP, "Mining History": mining_history_window._HELP + mining_history_window._HELP_SPACE,
              "Mining History (Surface)": mining_history_window._HELP + mining_history_window._HELP_SURFACE, "Space Mining Book": mining_ring_book._HELP,
              "What pays": mining_what_pays_dialog._HELP, "Notes": notes_window._HELP, "Powerplay session": powerplay_window._HELP,
              "Rare Goods Finder": rare_goods_window.RareGoodsWindow._HELP, "Route Planner": route_planner_window.HELP, "Marks": surface_marks_window._HELP,
              "Trade History": trade_history_window.HELP, "Watch list": trade_watch_window._HELP, "Surface Mining Live": mining_live_window._SURFACE_HELP}
for name, items in help_texts.items():
    shell = WindowShell(host, name, "", size=(600, 300), min_size=(400, 200))
    shell.add_help(name + " help", items)
    shell._show_help()
    F.pump(root, 2)
    window = shell._help_window
    for kind, text in F.check_window(root, window, window.winfo_reqwidth(), window.winfo_reqheight(), wide=False):
        if kind in F.FAIL_KINDS:
            problems.append(f"{name} help: {kind}: {text}")
    if window.winfo_reqwidth() > 760 or window.winfo_reqheight() > root.winfo_screenheight() - 80:
        problems.append(f"{name} help: the window asks for {window.winfo_reqwidth()}x{window.winfo_reqheight()} px")
    shell.close()

root.destroy()
for line in notes:
    print("note:", line)
if problems:
    print("PROBLEMS:\n  " + "\n  ".join(problems))
    sys.exit(1)
print("WINDOW FIT MORE OK")
