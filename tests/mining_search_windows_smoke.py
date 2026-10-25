"""Opens the real Find Best Price, Check Ring Reserve Level and Find Nearby Hotspots windows (plugin/mining_price_finder_dialog.py, plugin/mining_reserve_lookup_dialog.py,
plugin/mining_hotspot_finder_dialog.py) with EDMC stubbed and the network replaced:
the results fill a sortable table, the Demand/Supply heading follows the choice, "This system only" is passed on, a copy goes to the clipboard, a failed lookup says so, and the windows survive
the Mining panel's content frame being destroyed (they hang off the main window). Run by test_mining_search_windows_smoke in a subprocess so the stand-ins never leak into other tests. Exits 0 if
everything holds, 1 if not, 77 if Tk is unavailable."""
import quiet_tk  # noqa: F401  (keeps the test windows from taking focus)
import os
import sys
import time
import types
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
saved = {}


class Cfg:
    default_journal_dir = ""

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
cfgmod.user_agent = "WFMT-test"
cfgmod.appversion = lambda: "5.13.0"
sys.modules["config"] = cfgmod

try:
    root = tk.Tk()
except tk.TclError:
    print("no display available")
    sys.exit(77)
root.withdraw()

from plugin import mining_hotspot_finder_dialog as HF, mining_location, mining_price_finder_dialog as PF, mining_reserve_lookup_dialog as RL, mining_spansh_client as SC  # noqa: E402

problems = []


def check(condition, message):
    if not condition:
        problems.append(message)


def pump(seconds=0.0):
    end = time.time() + seconds
    root.update()
    while time.time() < end:
        root.update()
        time.sleep(0.01)


def wait_for(condition, seconds=5.0):
    end = time.time() + seconds
    while time.time() < end:
        pump(0.02)
        if condition():
            return True
    return False


def station(name, system, price, qty, pads=(0, 1, 3), planetary=False):
    return SC.StationPrice(station=name, system=system, station_type="Coriolis Starport", distance_ly=12.34, distance_to_arrival_ls=567.0, is_planetary=planetary,
                           price=price, quantity=qty, small_pads=pads[0], medium_pads=pads[1], large_pads=pads[2])


calls = []


def fake_search(origin, commodity, transaction, distance, **kw):
    calls.append((origin, commodity, transaction, distance, kw))
    if commodity == "Boom":
        raise RuntimeError("network down")
    if kw.get("this_system_only"):
        return [station("Here Port", origin, 51000, 900)]
    return [station("Far Port", "Other", 49000, 120, planetary=True), station("Near Port", "Sol", 51000, 4500)]


PF.search_stations = fake_search
mining_location.set_current_system("Sol")
copied = []
with mock.patch("plugin.panelkit.copy_to_clipboard", lambda widget, text: copied.append(text) or True):
    # --- the price window -----------------------------------------------------------------------------------------------
    panel_content = tk.Frame(root)
    PF.open_price_finder_dialog(panel_content, suggested_commodities=["Platinum"])
    win = PF._window
    check(win is not None and win.alive, "the price window did not open")
    for child in panel_content.winfo_children():
        child.destroy()
    panel_content.destroy()
    pump()
    check(win.alive, "the price window was destroyed with the panel's content frame")
    check(win._origin.get() == "Sol", f"the search starts from the current system: {win._origin.get()!r}")
    check(win._choices(win._suggested)[0] == "Platinum", "what was refined this run leads the commodity list")

    win._search()
    check("Type a commodity" in win._shell._status.cget("text"), "searching with no commodity says what to do")
    win._commodity.set("Gold")
    win._search()
    check(wait_for(lambda: len(win._table) == 2), f"the results did not fill: {len(win._table)} rows")
    check(calls[-1][:4] == ("Sol", "Gold", "Sell", 50.0) and calls[-1][4].get("this_system_only") is False, f"the default search was wrong: {calls[-1]}")
    check("pay the most for Gold" in win._heading.cget("text") and "within 50 ly of Sol" in win._heading.cget("text"), f"the heading: {win._heading.cget('text')!r}")
    check(calls[-1][4].get("min_quantity") == 1 and calls[-1][4].get("exclude_carriers") is True and "Drake-Class Carrier" not in calls[-1][4].get("station_types", []),
          f"no hold: a floor of 1 t and carriers left out: {calls[-1][4]}")
    check(win._minimum.get() == "1", f"the minimum starts at 1: {win._minimum.get()!r}")
    first = win._table._rows["p0"].values
    check(first[2] == "49,000" and first[3] == "120" and first[6] == "Large" and first[7].startswith("Ground"), f"the first row reads wrong: {first}")
    win._table.select("p1", notify=False)
    win._copy("system")
    win._copy("station")
    check(copied == ["Sol", "Near Port"], f"copying gave {copied}")

    with mock.patch.object(PF.pays, "hold", lambda: {"gold": 7, "lowtemperaturediamond": 3}):
        win._commodity.set("gold")
        check(win._minimum.get() == "7", f"the minimum follows the hold: {win._minimum.get()!r}")
        win._commodity.set("Low Temperature Diamonds")
        check(win._minimum.get() == "3", f"the hold is matched by name: {win._minimum.get()!r}")
        win._commodity.set("Gold")
        win._minimum.set("abc")
        before = len(calls)
        win._search()
        check(len(calls) == before and "whole number" in win._shell._status.cget("text"), "a minimum that is not a number should be refused")
        win._minimum.set("0")
        win._search()
        check(len(calls) == before, "a minimum of 0 should be refused")
        win._minimum.set("25")
        win._search()
        check(wait_for(lambda: len(calls) == before + 1 and calls[-1][4].get("min_quantity") == 25), f"the typed minimum was not sent: {calls[-1]}")
        check(wait_for(lambda: not win._busy), "the search with a typed minimum did not finish")
        win._minimum_typed = True
        win._commodity.set("Painite")
        check(win._minimum.get() == "25", "a typed minimum is kept when the commodity changes")
        win._minimum_typed = False
        win._commodity.set("Gold")
    win._transaction.set(PF.BUYING)
    win._set_amount_heading()
    check(win._minimum_label.cget("text") == "Minimum supply (t)", "buying should read Minimum supply")
    check(win._table._header_labels[3].cget("text").startswith("Supply"), "buying should read Supply, not Demand")
    win._where.set(PF.THIS_SYSTEM)
    win._search()
    check(wait_for(lambda: calls[-1][4].get("this_system_only") is True), "This system only was not passed on")
    check(wait_for(lambda: len(win._table) == 1), "the this-system result did not fill")
    check("in Sol" in win._heading.cget("text"), f"the this-system heading: {win._heading.cget('text')!r}")

    win._commodity.set("Boom")
    win._search()
    check(wait_for(lambda: "search failed" in win._shell._status.cget("text").lower()), f"a failed search should say so: {win._shell._status.cget('text')!r}")
    check(win._search_button._enabled, "the Search button stays disabled after a failure")
    win.close()

    # --- the reserve window ---------------------------------------------------------------------------------------------
    RAW = [{"name": "Sol 5", "reserveLevel": "PristineResources", "rings": [{"name": "Sol 5 A Ring", "type": "Metallic"}, {"name": "Sol 5 B Ring", "type": "Icy"}]},
           {"name": "Sol 6", "reserveLevel": None, "rings": [{"name": "Sol 6 A Ring", "type": "Rocky"}]}, {"name": "Sol 3", "rings": []}]
    RL.fetch_bodies = lambda system: None if system == "Nowhere" else RAW
    RL.open_reserve_lookup_dialog(tk.Frame(root))
    rw = RL._window
    check(rw is not None and rw.alive, "the reserve window did not open")
    rw._system.set("Sol")
    rw._name.set("")
    rw._search()
    check(wait_for(lambda: len(rw._table) == 3), f"the whole-system list did not fill: {len(rw._table)} rows")
    values = [rw._table._rows[f"r{i}"].values for i in range(3)]
    check(values[0][2] == "Pristine" and values[0][4] == "Metallic", f"first ring reads wrong: {values[0]}")
    check(values[1][4] == RL.NOT_METALLIC and values[2][2] == "Unknown", f"non-Metallic and unknown reserve not shown: {values[1:]}")
    check("2 ringed bodies" in rw._heading.cget("text"), f"the heading: {rw._heading.cget('text')!r}")
    rw._name.set("sol 5 b ring")
    rw._search()
    check(wait_for(lambda: len(rw._table) == 2 and "Sol 5" in rw._heading.cget("text")), "a ring name should list that body's rings")
    rw._name.set("Nothing Here")
    rw._search()
    check(wait_for(lambda: len(rw._table) == 0 and "no ringed body named" in rw._shell._status.cget("text")), f"not-found message: {rw._shell._status.cget('text')!r}")
    rw._system.set("Nowhere")
    rw._search()
    check(wait_for(lambda: "lookup failed" in rw._shell._status.cget("text").lower()), f"a failed lookup should say so: {rw._shell._status.cget('text')!r}")
    rw.close()

    # --- the hotspot finder ---------------------------------------------------------------------------------------------
    ring_calls = []

    def fake_rings(origin, material, distance, **kw):
        ring_calls.append((origin, material, distance, kw))
        if material == "Boom":
            raise RuntimeError("network down")
        return [SC.RingHotspot(system="Far", body="Far 2", ring_name="Far 2 A Ring", distance_ly=61.25, distance_to_arrival_ls=1500.0, reserve_level="Pristine", hotspot_count=3),
                SC.RingHotspot(system="Near", body="Near 1", ring_name="Near 1 B Ring", distance_ly=4.5, distance_to_arrival_ls=80.0, reserve_level="Unknown", hotspot_count=1)]

    HF.search_rings = fake_rings
    HF.open_hotspot_finder_dialog(tk.Frame(root))
    hw = HF._window
    check(hw is not None and hw.alive, "the hotspot window did not open")
    check(hw._origin.get() == "Sol", f"the hotspot search starts from the current system: {hw._origin.get()!r}")
    hw._search()
    check("Type a material" in hw._shell._status.cget("text"), "searching with no material says what to do")
    hw._material.set("Painite")
    hw._search()
    check(wait_for(lambda: len(hw._table) == 2), f"the hotspot results did not fill: {len(hw._table)} rows")
    check(ring_calls[-1][:3] == ("Sol", "Painite", 100.0), f"the default hotspot search was wrong: {ring_calls[-1]}")
    check("Painite hotspots, within 100 ly of Sol" in hw._heading.cget("text"), f"the hotspot heading: {hw._heading.cget('text')!r}")
    check(hw._table._rows["h0"].values[3:] == ["3", "61.2", "1,500", "Pristine"], f"the first hotspot row reads wrong: {hw._table._rows['h0'].values}")
    copied.clear()
    hw._table.select("h1", notify=False)
    hw._copy("ring")
    hw._copy("body")
    hw._copy("system")
    check(copied == ["Near 1 B Ring", "Near 1", "Near"], f"copying gave {copied}")
    hw._where.set("Within 500 ly")
    hw._search()
    check(wait_for(lambda: ring_calls[-1][2] == 500.0), "the chosen distance was not used")
    check(wait_for(lambda: not hw._busy), "the hotspot search did not finish")
    hw._material.set("Boom")
    hw._search()
    check(wait_for(lambda: "search failed" in hw._shell._status.cget("text").lower()), f"a failed hotspot search should say so: {hw._shell._status.cget('text')!r}")
    check(hw._search_button._enabled, "the hotspot Search button stays disabled after a failure")
    hw.close()

root.destroy()
if problems:
    print("PROBLEMS:")
    for p in problems:
        print("  -", p)
    sys.exit(1)
print("SEARCH WINDOWS OK")
