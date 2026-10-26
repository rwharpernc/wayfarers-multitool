"""Builds the colonization pop-out windows (Colonization Sites with its where-to-buy results, Colonization History and Planned Builds) with EDMC stubbed and long data
(60-character construction site and station names, 40-character system names, tonnages in the millions), and runs the layout checker (window_fit_check.py) at the window's
minimum size, 640 px wide and 1600 px wide. Fails on text cut off, controls pushed outside the window, labels that cannot wrap and tables whose columns do not fit or do
not use a wide window. Run by test_window_fit_colonization_smoke.py in a subprocess so the stand-ins never leak into other tests. Exits 0 if everything holds, 1 if not,
77 if Tk is unavailable."""
import quiet_tk  # noqa: F401  (keeps the test windows from taking focus)
import os
import sys
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

from plugin import (colonization, colonization_builds_window as B, colonization_carrier, colonization_data, colonization_history_window as HW,  # noqa: E402
                    colonization_projects_window as PW, colonization_sources as S, colonization_window as W, rcc_client)

problems, notes = [], []
SITE = "Orbital Construction Site: " + F.STATION[:33]       # 60 characters
COMMODITIES = ("Steel", "Water", "Aluminium", "Titanium", "Polymers", "Copper", "Ceramic Composites", "Insulating Membrane", "Liquid Oxygen", "Semiconductors",
               "Superconductors", "Fruit and Vegetables", "Computer Components", "Building Fabricators", "Surface Stabilisers", "Structural Regulators")


def make(market_id, name, complete=False):
    entry = {"MarketID": market_id, "ConstructionProgress": 0.4, "ConstructionComplete": complete,
             "ResourcesRequired": [{"Name": f"${c.lower().replace(' ', '')}_name;", "Name_Localised": c, "RequiredAmount": 12_345_678, "ProvidedAmount": 1000}
                                   for c in COMMODITIES]}
    return colonization.apply_depot_event(entry, None, name=name, system=F.SYSTEM)


repo_sites = colonization_data.SiteRepository()
repo_sites.upsert(F.COMMANDER, make(1, SITE))
repo_sites.upsert(F.COMMANDER, make(2, SITE[::-1], complete=True))
repo_sites.upsert(F.COMMANDER, make(3, "Other " + SITE))
carrier = colonization_carrier.CarrierCargo()
carrier.note_carrier(F.COMMANDER)
carrier.commit()


def fake_find(system, commodity, **kwargs):
    near = S.Source(F.STATION, F.SYSTEM, "Planetary Outpost of the Long Name Kind", False, True, "Large", 12345.6, 123456.0, 4100, 9_000_000)
    far = S.Source(F.STATION[::-1], F.SYSTEM[::-1], "Coriolis Starport", False, False, "Medium", 22345.6, 1200.0, 3800, 50)
    fc = S.Source("K7X-LLL " + F.STATION[:30], F.SYSTEM, "Drake-Class Carrier", True, False, "Large", 32345.6, 0.0, 3000, 20)
    return S.SearchResult([near, far], [fc] if kwargs.get("include_carriers") else [])


def fake_whole(system, commodities, **kwargs):
    kwargs["progress"](0, len(commodities), commodities[0])
    found = [(name, fake_find(system, name, include_carriers=True)) for name in commodities[:6]]
    return S.WholeListResult(found=found, failed=[])


W.sources.find = fake_find
W.sources.find_whole_list = fake_whole


def settle(done):
    end = time.monotonic() + 5
    while time.monotonic() < end and not done():
        F.pump(root, 1)
        time.sleep(0.02)
    F.pump(root)


# --- Colonization Sites ----------------------------------------------------------------------------------------------------------------
W.show(root, repo_sites, F.COMMANDER, {"steel": 500, "water": 50}, carrier, lambda: 784, lambda: F.SYSTEM, lambda: (F.STATION, frozenset({"steel"})))
window = W._window
F.pump(root)
window._system_var.set(F.SYSTEM)
window._commodity_table.select("1:steel", notify=True)
window._pad.set("Large only")
window._carriers_var.set(True)
window._on_find()
settle(lambda: window._find_button._enabled)
views = [("results", lambda: None)]


def whole():
    window._on_find_all()
    settle(lambda: window._whole_job is None)


views.append(("find all", whole))
F.check_views(root, window._toplevel, "Colonization Sites", views, problems, notes)
window.close()

# --- Colonization History --------------------------------------------------------------------------------------------------------------
record = {"journal_at": "", "first": "2026-09-01T00:00:00Z", "last": "2026-10-20T00:00:00Z", "deliveries": 12_345_678, "tons": 12_345_678_901,
          "by_commodity": {c.lower(): {"label": c + " of the Long Name Kind", "tons": 12_345_678_901} for c in COMMODITIES},
          "by_site": {"1": 12_345_678_901, "2": 5, "99": 7}, "by_day": {f"2026-10-{n:02d}": 12_345_678_901 for n in range(1, 21)},
          "claims": {"made": 12_345, "released": 11_000, "beacons": 999, "at": ""}, "site_names": {"99": SITE + " (" + F.SYSTEM + ")"}}
sites = repo_sites.for_cmdr(F.COMMANDER)
HW.show(root, lambda: (F.COMMANDER, sites, record))
hwin = HW._window
F.pump(root)
tabs = hwin._shell.body.winfo_children()[0]
F.check_views(root, hwin._shell.window, "Colonization History", F.tab_views(tabs), problems, notes)
HW.close()

# --- Planned Builds --------------------------------------------------------------------------------------------------------------------


def fake_system(system):
    return rcc_client.parse_system({"name": system, "architect": F.COMMANDER, "open": False, "sites": [
        {"name": SITE, "status": "plan", "buildType": "hermes_of_the_very_long_unknown_type_name", "bodyNum": 31},
        {"name": SITE[::-1], "status": "build", "buildType": "no_truss", "bodyNum": 7, "marketId": 1},
        {"name": "Elsewhere", "status": "complete", "buildType": "dysnomia", "bodyNum": 7, "marketId": 999}]})


B.show(root, F.SYSTEM, lambda: frozenset({1}), fake_system)
bwin = B._window
settle(lambda: len(bwin._table) == 3)
F.check_views(root, bwin._shell.window, "Planned Builds", None, problems, notes)
B.close()

# --- My Projects -----------------------------------------------------------------------------------------------------------------------
long_name = SITE * 3
rcc_client.fetch_active = lambda cmdr: rcc_client.parse_project_views([
    {"buildId": f"b{n}", "buildName": long_name + str(n), "systemName": F.SYSTEM * 3, "buildType": "hermes_of_the_very_long_unknown_type_name",
     "marketId": 1, "sumNeed": 12_345_678_901, "maxNeed": 12_345_678_901 * 2, "commodities": {"steel": 12_345_678_901}} for n in range(30)])
rcc_client.fetch_hidden = lambda cmdr: ["b1"]
rcc_client.fetch_primary = lambda cmdr: "b2"
PW.show(root, lambda: F.COMMANDER * 3, lambda: frozenset({1}), lambda: 100)
pwin = PW._window
settle(lambda: len(pwin._table) == 30)
F.check_views(root, pwin._shell.window, "My Projects", None, problems, notes)
PW.close()

root.destroy()
for line in notes:
    print("note:", line)
if problems:
    print("PROBLEMS:\n  " + "\n  ".join(problems))
    sys.exit(1)
print("WINDOW FIT COLONIZATION OK")
